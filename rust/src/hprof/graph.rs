use std::{
    collections::{HashMap, HashSet},
    rc::Rc,
};

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

pub struct ConsNode<T>(T, Option<ConsList<T>>);
pub type ConsList<T> = Rc<ConsNode<T>>;

fn cons<T>(val: T) -> ConsList<T> {
    Rc::new(ConsNode(val, None))
}

fn cons_list<T>(val: T, next: ConsList<T>) -> ConsList<T> {
    Rc::new(ConsNode(val, Some(next)))
}

pub fn to_vec<T: Clone>(list: &ConsList<T>) -> Vec<T> {
    let mut out = Vec::new();
    let mut current: Option<&ConsList<T>> = Some(list);

    while let Some(node_rc) = current {
        let ConsNode(ref head, ref tail) = **node_rc;
        out.push(head.clone());
        current = tail.as_ref();
    }

    out
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

pub fn find_paths<T: Id, U: Fn(T) -> bool>(
    graph: &[(T, T)],
    root_pred: U,
    start_nodes: &[T],
    max_paths: usize,
) -> Vec<Vec<ConsList<T>>> {
    let mut reachable: IntMap<T, Vec<ConsList<T>>> = IntMap::default();
    let mut temp_vis: IntSet<T> = IntSet::default();

    fn dfs<T: Id, U: Fn(T) -> bool>(
        u: T,
        graph: &[(T, T)],
        root_pred: &U,
        reachable: &mut IntMap<T, Vec<ConsList<T>>>,
        temp_vis: &mut IntSet<T>,
        max_paths: usize,
    ) -> Vec<ConsList<T>> {
        if let Some(x) = reachable.get(&u) {
            return x.clone();
        }

        if root_pred(u) {
            reachable.insert(u, vec![cons(u)]);
            return vec![cons(u)];
        }

        if temp_vis.contains(&u) {
            return vec![];
        }

        temp_vis.insert(u);

        let mut found = vec![];

        let mut idx = graph.partition_point(|&(src, _)| src < u);

        while idx < graph.len() && graph[idx].0 == u {
            for node in dfs(graph[idx].1, graph, root_pred, reachable, temp_vis, max_paths) {
                found.push(cons_list(u, node));
                if found.len() >= max_paths {
                    break;
                }
            }

            if found.len() >= max_paths {
                break;
            }

            idx += 1;
        }

        temp_vis.remove(&u);

        reachable.insert(u, found.clone());

        found
    }

    let mut res = Vec::new();
    for &s in start_nodes {
        res.push(dfs(s, graph, &root_pred, &mut reachable, &mut temp_vis, max_paths));
    }

    res
}
