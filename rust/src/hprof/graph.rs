use std::collections::{HashMap, HashSet, VecDeque};

use crate::hprof::id::Id;

pub type IntMap<K, V> = HashMap<K, V>;
pub type IntSet<K> = HashSet<K>;

pub fn clean_graph<T: Id + Ord + Copy>(edges: &mut Vec<(T, T)>) {
    if edges.is_empty() {
        return;
    }

    edges.sort_unstable();
    edges.dedup();
    edges.shrink_to_fit();
}

pub fn is_reachable<T: Id, U: Fn(T) -> bool>(graph: &[(T, T)], root_pred: U, start_nodes: &[T]) -> Vec<bool> {
    let mut reachable: IntMap<T, bool> = IntMap::default();
    let mut temp_vis: IntSet<T> = IntSet::default();

    fn dfs<T: Id, U: Fn(T) -> bool>(
        u: T,
        graph: &[(T, T)],
        root_pred: &U,
        reachable: &mut IntMap<T, bool>,
        temp_vis: &mut IntSet<T>,
    ) -> bool {
        if let Some(x) = reachable.get(&u) {
            return *x;
        }

        if root_pred(u) {
            reachable.insert(u, true);
            return true;
        }

        if temp_vis.contains(&u) {
            return false;
        }

        temp_vis.insert(u);

        let mut found = false;

        let mut idx = graph.partition_point(|&(src, _)| src < u);

        while idx < graph.len() && graph[idx].0 == u {
            if dfs(graph[idx].1, graph, root_pred, reachable, temp_vis) {
                found = true;
                break;
            }

            idx += 1;
        }

        temp_vis.remove(&u);

        reachable.insert(u, found);

        found
    }

    let mut res = Vec::new();
    for &s in start_nodes {
        res.push(dfs(s, graph, &root_pred, &mut reachable, &mut temp_vis));
    }

    res
}

/// BFS shortest path from `start` through back-reference edges to any node matching `root_pred`.
/// Returns the path as [start, ..., root], or an empty Vec if no path exists.
pub fn find_shortest_path<T: Id, U: Fn(T) -> bool>(graph: &[(T, T)], root_pred: U, start: T) -> Vec<T> {
    let mut came_from: IntMap<T, Option<T>> = IntMap::default();
    let mut queue: VecDeque<T> = VecDeque::new();

    came_from.insert(start, None);
    queue.push_back(start);

    while let Some(u) = queue.pop_front() {
        if root_pred(u) {
            let mut path = Vec::new();
            let mut cur = u;
            loop {
                path.push(cur);
                match came_from[&cur] {
                    None => break,
                    Some(prev) => cur = prev,
                }
            }
            path.reverse();
            return path;
        }

        let mut idx = graph.partition_point(|&(src, _)| src < u);
        while idx < graph.len() && graph[idx].0 == u {
            let v = graph[idx].1;
            if !came_from.contains_key(&v) {
                came_from.insert(v, Some(u));
                queue.push_back(v);
            }
            idx += 1;
        }
    }

    vec![]
}
