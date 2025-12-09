use std::{
    cell::{OnceCell, RefCell},
    io::{Error, Read},
    iter,
};

use anyhow::{Result, anyhow};
use byteorder::{BigEndian, ReadBytesExt};
use itertools::izip;
use phf::phf_map;
use smallvec::SmallVec;

use crate::{
    graph::{IntMap, IntSet, clean_graph, find_paths, is_reachable, to_vec},
    id::Id,
};
fn read_nocopy<'a>(this: &mut &'a [u8], size: usize) -> Result<&'a [u8], Error> {
    this.split_off(..size).ok_or(Error::new(
        std::io::ErrorKind::UnexpectedEof,
        "not enough contents left in buffer",
    ))
}

enum JVMValue<T: Id> {
    Obj(T),
    Bool(bool),
    Char(u16), // java chars are u16
    Float(f32),
    Double(f64),
    Byte(i8),
    Short(i16),
    Int(i32),
    Long(i64),
}

impl<T: Id> JVMValue<T> {
    fn read(reader: &mut &[u8]) -> Result<Self> {
        Self::read_with_type(reader.read_u8()?, reader)
    }

    fn read_with_type(ty: u8, reader: &mut &[u8]) -> Result<Self> {
        Ok(match ty {
            2 => JVMValue::Obj(T::read_from(reader)?),
            4 => JVMValue::Bool(reader.read_u8()? != 0),
            5 => JVMValue::Char(reader.read_u16::<BigEndian>()?),
            6 => JVMValue::Float(reader.read_f32::<BigEndian>()?),
            7 => JVMValue::Double(reader.read_f64::<BigEndian>()?),
            8 => JVMValue::Byte(reader.read_i8()?),
            9 => JVMValue::Short(reader.read_i16::<BigEndian>()?),
            10 => JVMValue::Int(reader.read_i32::<BigEndian>()?),
            11 => JVMValue::Long(reader.read_i64::<BigEndian>()?),
            x => return Err(anyhow!("unknown jvm value type: {x}")),
        })
    }
}

struct JVMClass<T: Id> {
    statics: SmallVec<[(T, JVMValue<T>); 4]>,
    instance: SmallVec<[(T, u8); 8]>,
}

#[repr(packed)]
struct JVMObj<'a, T: Id> {
    st_seqial: u32,
    data: JVMObjData<'a, T>,
}

enum JVMObjData<'a, T: Id> {
    Obj { class: T, fields: &'a [u8] },
    Array { class: T, entries: &'a [u8] },
    PrimVec { ty: u8, entries: &'a [u8] },
}

trait HeapDumpRecord<'a, T: Id>: Sized {
    const ID: u8;
    fn read(cur: &mut &'a [u8]) -> Result<Self>;
}

// HPROF_GC_ROOT_JNI_GLOBAL

struct GcRootJniGlobal<T: Id> {
    id: T,
    jni_global_ref_id: T,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootJniGlobal<T> {
    const ID: u8 = 0x01;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
            jni_global_ref_id: Id::read_from(cur)?,
        })
    }
}

// HPROF_GC_ROOT_JNI_LOCAL

struct GcRootJniLocal<T: Id> {
    id: T,
    thread_seq: u32,
    frame_num: u32,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootJniLocal<T> {
    const ID: u8 = 0x02;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
            thread_seq: cur.read_u32::<BigEndian>()?,
            frame_num: cur.read_u32::<BigEndian>()?,
        })
    }
}

// HPROF_GC_ROOT_JAVA_FRAME

struct GcRootJavaFrame<T> {
    id: T,
    thread_seq: u32,
    frame_num: u32,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootJavaFrame<T> {
    const ID: u8 = 0x03;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
            thread_seq: cur.read_u32::<BigEndian>()?,
            frame_num: cur.read_u32::<BigEndian>()?,
        })
    }
}

// HPROF_GC_ROOT_NATIVE_STACK

struct GcRootNativeStack<T> {
    id: T,
    thread_seq: u32,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootNativeStack<T> {
    const ID: u8 = 0x04;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
            thread_seq: cur.read_u32::<BigEndian>()?,
        })
    }
}

// HPROF_GC_ROOT_STICKY_CLASS

struct GcRootStickyClass<T> {
    id: T,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootStickyClass<T> {
    const ID: u8 = 0x05;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
        })
    }
}

// HPROF_GC_ROOT_THREAD_BLOCK

struct GcRootThreadBlock<T> {
    id: T,
    thread_seq: u32,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootThreadBlock<T> {
    const ID: u8 = 0x06;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
            thread_seq: cur.read_u32::<BigEndian>()?,
        })
    }
}

// HPROF_GC_ROOT_MONITOR_USED

struct GcRootMonitorUsed<T> {
    id: T,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootMonitorUsed<T> {
    const ID: u8 = 0x07;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
        })
    }
}

// HPROF_GC_ROOT_THREAD_OBJ

struct GcRootThreadObj<T: Id> {
    id: T,
    seq: u32,
    stacktrace_seq: u32,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcRootThreadObj<T> {
    const ID: u8 = 0x08;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        Ok(Self {
            id: Id::read_from(cur)?,
            seq: cur.read_u32::<BigEndian>()?,
            stacktrace_seq: cur.read_u32::<BigEndian>()?,
        })
    }
}

// HPROF_GC_CLASS_DUMP

struct GcClassDump<T: Id> {
    id: T,
    stacktrace_seq: u32,
    super_id: T,
    class_loader_id: T,
    signers_id: T,
    protection_domain_id: T,
    inst_size: u32,
    statics: SmallVec<[(T, JVMValue<T>); 4]>,
    instance: SmallVec<[(T, u8); 8]>,
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcClassDump<T> {
    const ID: u8 = 0x20;

    fn read(cur: &mut &[u8]) -> Result<Self> {
        let id = T::read_from(cur)?;
        let stacktrace_seq = cur.read_u32::<BigEndian>()?;
        let super_id = T::read_from(cur)?;
        let class_loader_id = T::read_from(cur)?;
        let signers_id = T::read_from(cur)?;
        let protection_domain_id = T::read_from(cur)?;
        let _ = T::read_from(cur)?;
        let _ = T::read_from(cur)?;
        let inst_size = cur.read_u32::<BigEndian>()?;

        let cp_cnt = cur.read_u16::<BigEndian>()?;
        assert!(cp_cnt == 0);

        let static_cnt = cur.read_u16::<BigEndian>()?;
        let mut statics = SmallVec::new();
        statics.reserve(static_cnt.into());
        for _ in 0..static_cnt {
            let name = T::read_from(cur)?;
            let value = JVMValue::<T>::read(cur)?;
            statics.push((name, value));
        }

        let inst_cnt = cur.read_u16::<BigEndian>()?;
        let mut instance = SmallVec::new();
        instance.reserve(inst_cnt.into());
        for _ in 0..inst_cnt {
            let name = T::read_from(cur)?;
            let ty = cur.read_u8()?;
            instance.push((name, ty));
        }

        Ok(Self {
            id,
            stacktrace_seq,
            super_id,
            class_loader_id,
            signers_id,
            protection_domain_id,
            inst_size,
            statics,
            instance,
        })
    }
}

impl<T: Id> GcClassDump<T> {
    fn iter_fields<F: FnMut(T, T, JVMValue<T>) -> ()>(
        &self,
        mut data: &[u8],
        classes: &IntMap<T, GcClassDump<T>>,
        mut handler: F,
    ) -> Result<()> {
        let mut class = self;

        loop {
            for (name_id, ty) in &class.instance {
                handler(
                    class.id,
                    *name_id,
                    JVMValue::read_with_type(*ty, &mut data)?,
                )
            }

            if class.super_id == T::NULL {
                break;
            }

            class = classes.get(&class.super_id).unwrap();
        }

        debug_assert!(data.is_empty());
        Ok(())
    }
}

// HPROF_GC_INSTANCE_DUMP

struct GcInstanceDump<'a, T: Id> {
    id: T,
    stacktrace_seq: u32,
    class_id: T,
    data: &'a [u8],
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcInstanceDump<'a, T> {
    const ID: u8 = 0x21;

    fn read(cur: &mut &'a [u8]) -> Result<Self> {
        Ok(Self {
            id: T::read_from(cur)?,
            stacktrace_seq: cur.read_u32::<BigEndian>()?,
            class_id: T::read_from(cur)?,
            data: {
                let n = cur.read_u32::<BigEndian>()?;
                read_nocopy(cur, n.try_into()?)?
            },
        })
    }
}

// HPROF_GC_OBJ_ARRAY_DUMP

struct GcObjArrayDump<'a, T: Id> {
    id: T,
    stacktrace_seq: u32,
    class_id: T,
    data: &'a [u8],
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcObjArrayDump<'a, T> {
    const ID: u8 = 0x22;

    fn read(cur: &mut &'a [u8]) -> Result<Self> {
        let id = T::read_from(cur)?;
        let stacktrace_seq = cur.read_u32::<BigEndian>()?;
        let len: usize = cur.read_u32::<BigEndian>()?.try_into()?;
        let class_id = T::read_from(cur)?;
        Ok(Self {
            id,
            stacktrace_seq,
            class_id,
            data: read_nocopy(cur, len * size_of::<T>())?,
        })
    }
}

// HPROF_GC_PRIM_ARRAY_DUMP

struct GcPrimArrayDump<'a, T: Id> {
    id: T,
    stacktrace_seq: u32,
    ty: u8,
    data: &'a [u8],
}

impl<'a, T: Id> HeapDumpRecord<'a, T> for GcPrimArrayDump<'a, T> {
    const ID: u8 = 0x23;

    fn read(cur: &mut &'a [u8]) -> Result<Self> {
        let id = T::read_from(cur)?;
        let stacktrace_seq = cur.read_u32::<BigEndian>()?;
        let len: usize = cur.read_u32::<BigEndian>()?.try_into()?;
        let ty = cur.read_u8()?;

        let unit_len = match ty {
            4 | 8 => 1,
            5 | 9 => 2,
            6 | 10 => 4,
            7 | 11 => 8,
            _ => return Err(anyhow!("unknown prim array type: {ty}")),
        };

        Ok(Self {
            id,
            stacktrace_seq,
            ty,
            data: read_nocopy(cur, len * unit_len)?,
        })
    }
}

enum HeapDumpEntry<'a, T: Id> {
    RootJniGlobal(GcRootJniGlobal<T>),
    RootJniLocal(GcRootJniLocal<T>),
    RootJavaFrame(GcRootJavaFrame<T>),
    RootNativeStack(GcRootNativeStack<T>),
    RootStickyClass(GcRootStickyClass<T>),
    RootThreadBlock(GcRootThreadBlock<T>),
    RootMonitorUsed(GcRootMonitorUsed<T>),
    RootThreadObj(GcRootThreadObj<T>),
    ClassDump(GcClassDump<T>),
    InstanceDump(GcInstanceDump<'a, T>),
    ObjArrayDump(GcObjArrayDump<'a, T>),
    PrimArrayDump(GcPrimArrayDump<'a, T>),
}

enum GcRootData<T: Id> {
    RootJniGlobal(GcRootJniGlobal<T>),
    RootJniLocal(GcRootJniLocal<T>),
    RootJavaFrame(GcRootJavaFrame<T>),
    RootNativeStack(GcRootNativeStack<T>),
    RootStickyClass(GcRootStickyClass<T>),
    RootThreadBlock(GcRootThreadBlock<T>),
    RootMonitorUsed(GcRootMonitorUsed<T>),
    RootThreadObj(GcRootThreadObj<T>),
}

impl<T: Id> GcRootData<T> {
    fn id(&self) -> T {
        match self {
            GcRootData::RootJniGlobal(x) => x.id,
            GcRootData::RootJniLocal(x) => x.id,
            GcRootData::RootJavaFrame(x) => x.id,
            GcRootData::RootNativeStack(x) => x.id,
            GcRootData::RootStickyClass(x) => x.id,
            GcRootData::RootThreadBlock(x) => x.id,
            GcRootData::RootMonitorUsed(x) => x.id,
            GcRootData::RootThreadObj(x) => x.id,
        }
    }
}

impl<'a, T: Id> HeapDumpEntry<'a, T> {
    pub fn read(record: &mut &'a [u8]) -> Result<HeapDumpEntry<'a, T>> {
        let tag = record.read_u8()?;

        let entry = match tag {
            GcRootJniGlobal::<T>::ID => {
                HeapDumpEntry::RootJniGlobal(GcRootJniGlobal::read(record)?)
            }
            GcRootJniLocal::<T>::ID => HeapDumpEntry::RootJniLocal(GcRootJniLocal::read(record)?),
            GcRootJavaFrame::<T>::ID => {
                HeapDumpEntry::RootJavaFrame(GcRootJavaFrame::read(record)?)
            }
            GcRootNativeStack::<T>::ID => {
                HeapDumpEntry::RootNativeStack(GcRootNativeStack::read(record)?)
            }
            GcRootStickyClass::<T>::ID => {
                HeapDumpEntry::RootStickyClass(GcRootStickyClass::read(record)?)
            }
            GcRootThreadBlock::<T>::ID => {
                HeapDumpEntry::RootThreadBlock(GcRootThreadBlock::read(record)?)
            }
            GcRootMonitorUsed::<T>::ID => {
                HeapDumpEntry::RootMonitorUsed(GcRootMonitorUsed::read(record)?)
            }
            GcRootThreadObj::<T>::ID => {
                HeapDumpEntry::RootThreadObj(GcRootThreadObj::read(record)?)
            }
            GcClassDump::<T>::ID => HeapDumpEntry::ClassDump(GcClassDump::read(record)?),
            GcInstanceDump::<T>::ID => HeapDumpEntry::InstanceDump(GcInstanceDump::read(record)?),
            GcObjArrayDump::<T>::ID => HeapDumpEntry::ObjArrayDump(GcObjArrayDump::read(record)?),
            GcPrimArrayDump::<T>::ID => {
                HeapDumpEntry::PrimArrayDump(GcPrimArrayDump::read(record)?)
            }

            other => {
                return Err(anyhow!("Unknown heap dump tag: {other:#x}"));
            }
        };

        Ok(entry)
    }
}

#[derive(Clone, Copy)]
enum ClassNames {
    WorldServerClass = 0,
    DedicatedServerClass,
    CraftServerClass,
    CraftAsyncSchedulerClass,
    CraftSchedulerClass,
    ReferenceClass,
    Max,
}

// note: these names are dependent on the mappings, so we should be careful when upgrading mc
// versions
static CLASS_NAMES: phf::Map<&'static [u8], ClassNames> = phf_map! {
    b"net/minecraft/server/level/WorldServer" => ClassNames::WorldServerClass,
    b"net/minecraft/server/dedicated/DedicatedServer" => ClassNames::DedicatedServerClass,
    b"org/bukkit/craftbukkit/v1_20_R3/CraftServer" => ClassNames::CraftServerClass,
    b"org/bukkit/craftbukkit/v1_20_R3/scheduler/CraftAsyncScheduler" => ClassNames::CraftAsyncSchedulerClass,
    b"org/bukkit/craftbukkit/v1_20_R3/scheduler/CraftScheduler" => ClassNames::CraftSchedulerClass,
    b"java/lang/ref/Reference" => ClassNames::ReferenceClass
};

fn visit_prof<
    'a,
    T: Id,
    U: FnMut(T, &'a [u8]) -> (),
    V: FnMut(T, T) -> (),
    X: FnMut(GcRootData<T>) -> (),
    Y: FnMut(HeapDumpEntry<'a, T>) -> Result<()>,
>(
    mut file: &'a [u8],
    mut on_string: U,
    mut on_class: V,
    mut on_gc_root: X,
    mut on_heap_entry: Y,
) -> Result<()> {
    while !file.is_empty() {
        let tag = file.read_u8()?;
        let _ = file.read_u32::<BigEndian>()?;
        let len: usize = file.read_u32::<BigEndian>()?.try_into()?;
        let mut record = read_nocopy(&mut file, len)?;

        match tag {
            1 => {
                let id = T::read_from(&mut record)?;
                on_string(id, record);
            }
            2 => {
                let _ = record.read_u32::<BigEndian>()?;
                let obj_id = T::read_from(&mut record)?;
                let _ = record.read_u32::<BigEndian>()?;
                let name_id = T::read_from(&mut record)?;
                on_class(obj_id, name_id);
            }
            0x0c | 0x1c => {
                while !record.is_empty() {
                    match HeapDumpEntry::<T>::read(&mut record)? {
                        HeapDumpEntry::RootJniGlobal(root) => {
                            on_gc_root(GcRootData::RootJniGlobal(root))
                        }
                        HeapDumpEntry::RootJniLocal(root) => {
                            on_gc_root(GcRootData::RootJniLocal(root))
                        }
                        HeapDumpEntry::RootJavaFrame(root) => {
                            on_gc_root(GcRootData::RootJavaFrame(root))
                        }
                        HeapDumpEntry::RootNativeStack(root) => {
                            on_gc_root(GcRootData::RootNativeStack(root))
                        }
                        HeapDumpEntry::RootStickyClass(root) => {
                            on_gc_root(GcRootData::RootStickyClass(root))
                        }
                        HeapDumpEntry::RootThreadBlock(root) => {
                            on_gc_root(GcRootData::RootThreadBlock(root))
                        }
                        HeapDumpEntry::RootMonitorUsed(root) => {
                            on_gc_root(GcRootData::RootMonitorUsed(root))
                        }
                        HeapDumpEntry::RootThreadObj(root) => {
                            on_gc_root(GcRootData::RootThreadObj(root))
                        }
                        x => on_heap_entry(x)?,
                    }
                }
            }
            _ => {}
        }
    }

    Ok(())
}

fn do_read_prof<'a, T: Id>(file: &'a [u8]) -> Result<()> {
    use ClassNames::*;

    let str_dict = RefCell::new(IntMap::default());
    let mut classes = IntMap::default();
    let mut class_names = IntMap::default();
    let mut gc_roots: IntMap<_, SmallVec<[GcRootData<T>; 2]>> = IntMap::default();

    let mut edges: Vec<(T, T)> = Vec::new();
    let mut world_server_instances = Vec::new();

    let special_strings = vec![OnceCell::new(); Max as usize];
    let class_ids = vec![OnceCell::new(); Max as usize];

    let mut non_leak_root_sources = Vec::new();

    let mut leak_root_sources = Vec::new();

    let mut insert_edge = |child: T, parent: T| {
        if child == T::NULL {
            return;
        }
        // we want back refs, so child -> parent
        edges.push((child, parent));
    };

    let get_class_id = |id: ClassNames| *class_ids[id as usize].get().unwrap();

    eprintln!("parsing heap dump");

    visit_prof(
        file,
        |id, data| {
            str_dict.borrow_mut().insert(id, data);

            if let Some(x) = CLASS_NAMES.get(data) {
                let res = special_strings[*x as usize].set(id);
                debug_assert!(res.is_ok());
            }
        },
        |obj_id, name_id| {
            let res = class_names.insert(obj_id, name_id);
            debug_assert!(res.is_none());

            for (idx, v) in special_strings.iter().enumerate() {
                if name_id == *v.get().unwrap() {
                    let res = class_ids[idx].set(obj_id);
                    debug_assert!(res.is_ok());
                }
            }
        },
        |root: GcRootData<T>| {
            gc_roots
                .entry(root.id())
                .or_insert(SmallVec::new())
                .push(root);
        },
        |entry| {
            match entry {
                HeapDumpEntry::ClassDump(class) => {
                    for (_, static_value) in &class.statics {
                        if let JVMValue::Obj(child) = static_value {
                            insert_edge(*child, class.id);
                        }
                    }

                    insert_edge(class.super_id, class.id);
                    insert_edge(class.class_loader_id, class.id);
                    insert_edge(class.signers_id, class.id);
                    insert_edge(class.protection_domain_id, class.id);

                    let res = classes.insert(class.id, class);
                    debug_assert!(res.is_none());
                }
                HeapDumpEntry::InstanceDump(inst) => {
                    let class = classes.get(&inst.class_id).unwrap();

                    insert_edge(class.id, inst.id);

                    if inst.class_id == get_class_id(WorldServerClass) {
                        world_server_instances.push(inst.id);
                    } else if inst.class_id == get_class_id(DedicatedServerClass) {
                        class.iter_fields(inst.data, &classes, |_, name_id, value| {
                            if str_dict.borrow()[&name_id] == b"Q" {
                                if let JVMValue::Obj(child) = value {
                                    non_leak_root_sources.push(child);
                                    eprintln!(
                                        "found non-leak root: DedicatedServer#levels: {child:x}"
                                    );
                                }
                            }
                        })?;
                    } else if inst.class_id == get_class_id(CraftServerClass) {
                        class.iter_fields(inst.data, &classes, |_, name_id, value| {
                            if str_dict.borrow()[&name_id] == b"worlds" {
                                if let JVMValue::Obj(child) = value {
                                    non_leak_root_sources.push(child);
                                    eprintln!("found non-leak root: CraftServer#worlds: {child:x}");
                                }
                            }
                        })?;
                    } else if inst.class_id == get_class_id(CraftSchedulerClass)
                        || inst.class_id == get_class_id(CraftAsyncSchedulerClass)
                    {
                        eprintln!("found scheduler instance: {:x}", inst.id);
                        leak_root_sources.push(inst.id);
                    }

                    class.iter_fields(inst.data, &classes, |cl_id, _, value| {
                        // ignore weak, phantom, etc
                        if cl_id == get_class_id(ReferenceClass) {
                            return;
                        }

                        if let JVMValue::Obj(child) = value {
                            insert_edge(child, inst.id);
                        }
                    })?;
                }
                HeapDumpEntry::ObjArrayDump(arr) => {
                    let len = arr.data.len() / size_of::<T>();
                    let mut buf = arr.data;

                    insert_edge(arr.class_id, arr.id);

                    for _ in 0..len {
                        insert_edge(T::read_from(&mut buf)?, arr.id);
                    }
                }
                _ => {}
            }

            Ok(())
        },
    )?;

    eprintln!("clean graph");

    clean_graph(&mut edges);

    eprintln!("finding paths to root");

    eprintln!("found {:?} instances", world_server_instances.len());

    let globally_reachable = is_reachable(
        &edges,
        |f| gc_roots.contains_key(&f),
        &world_server_instances,
    );

    let non_leaked_instances = is_reachable(
        &edges,
        |f| non_leak_root_sources.contains(&f),
        &world_server_instances,
    );

    let mut leak_candidates = Vec::new();

    for (inst, global, non_leak) in izip!(
        world_server_instances.iter(),
        globally_reachable.iter(),
        non_leaked_instances.iter(),
    ) {
        if !*global {
            continue;
        }

        if *non_leak {
            continue;
        }

        leak_candidates.push(*inst);
    }

    eprintln!("finding leaked object paths-to-root");
    eprintln!("found {} likely leak candidates", leak_candidates.len());

    let candidate_paths: Vec<Vec<_>> = find_paths(
        &edges,
        |f| leak_root_sources.contains(&f),
        &leak_candidates,
        64,
    )
    .iter()
    .map(|f| f.iter().map(|f| to_vec(f)).collect())
    .collect();

    eprintln!("re-gathering instance data");

    drop(edges);

    let mut relevant_inst: IntSet<T> = IntSet::default();
    let mut inst_data: IntMap<T, HeapDumpEntry<'a, T>> = IntMap::default();
    relevant_inst.extend(candidate_paths.iter().map(|f| f).flatten().flatten());

    let mut on_data = |id: T, data: HeapDumpEntry<'a, T>| {
        if relevant_inst.contains(&id) {
            inst_data.insert(id, data);
        }
    };

    visit_prof(
        file,
        |_, _| {},
        |_, _| {},
        |_| {},
        |inst| {
            match inst {
                HeapDumpEntry::InstanceDump(inst) => {
                    on_data(inst.id, HeapDumpEntry::InstanceDump(inst))
                }
                HeapDumpEntry::ObjArrayDump(inst) => {
                    on_data(inst.id, HeapDumpEntry::ObjArrayDump(inst))
                }
                _ => {}
            }
            Ok(())
        },
    )?;

    for (paths, candidate) in izip!(candidate_paths.iter(), leak_candidates.iter()) {
        println!("{candidate:x}");

        if paths.is_empty() {
            println!("unk");
            println!()
        } else {
            for path in paths {
                for ele in path {
                    println!(
                        "{ele:x} {}",
                        match inst_data.get(ele) {
                            Some(HeapDumpEntry::InstanceDump(inst)) => {
                                let class = classes.get(&inst.class_id).unwrap();
                                let class_name_id = class_names.get(&class.id).unwrap();
                                let dict = str_dict.borrow();
                                let class_name = dict.get(&class_name_id).unwrap();
                                str::from_utf8(class_name)?.into()
                            }
                            Some(HeapDumpEntry::ObjArrayDump(inst)) => {
                                let class = classes.get(&inst.class_id).unwrap();
                                let class_name_id = class_names.get(&class.id).unwrap();
                                let dict = str_dict.borrow();
                                let class_name = dict.get(&class_name_id).unwrap();
                                format!("{}[]", str::from_utf8(class_name)?)
                            }
                            None => {
                                let class = classes.get(ele).unwrap();
                                let class_name_id = class_names.get(&class.id).unwrap();
                                let dict = str_dict.borrow();
                                let class_name = dict.get(&class_name_id).unwrap();
                                format!("Class<{}>", str::from_utf8(class_name)?)
                            }
                            _ => unreachable!(),
                        }
                    )
                }

                println!();
            }
        }
    }

    Ok(())
}

const HEADER: &[u8; 19] = b"JAVA PROFILE 1.0.2\0";

pub fn read_prof(mut hprof_file: &[u8]) -> Result<()> {
    let mut header = [0; HEADER.len()];
    hprof_file.read_exact(&mut header)?;

    if *HEADER != header {
        return Err(anyhow!(
            "bad header, expected {HEADER:?} but got {header:?}"
        ));
    }

    let id_size = hprof_file.read_u32::<BigEndian>()?;
    let micros = hprof_file.read_u64::<BigEndian>()?;

    if id_size == 4 {
        do_read_prof::<u32>(hprof_file)?;
    } else if id_size == 8 {
        do_read_prof::<u64>(hprof_file)?;
    } else {
        return Err(anyhow!("illegal id_size: {id_size}"));
    }

    Ok(())
}
