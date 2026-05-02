use std::{
    cell::{OnceCell, RefCell},
    io::{Error, Read},
};

#[cfg(target_os = "linux")]
use libc;

use anyhow::{Result, anyhow};
use byteorder::{BigEndian, ReadBytesExt};
use itertools::izip;
use phf::phf_map;
use smallvec::SmallVec;

use crate::hprof::{
    graph::{IntMap, IntSet, clean_graph, find_shortest_path, is_reachable},
    id::{Id, OopId},
};

mod graph;
mod id;

fn read_nocopy<'a>(this: &mut &'a [u8], size: usize) -> Result<&'a [u8], Error> {
    this.split_off(..size)
        .ok_or(Error::new(std::io::ErrorKind::UnexpectedEof, "not enough contents left in buffer"))
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
    fn iter_fields<F: FnMut(T, T, JVMValue<T>)>(
        &self,
        mut data: &[u8],
        classes: &IntMap<T, GcClassDump<T>>,
        mut handler: F,
    ) -> Result<()> {
        let mut class = self;

        loop {
            for (name_id, ty) in &class.instance {
                handler(class.id, *name_id, JVMValue::read_with_type(*ty, &mut data)?)
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
            data: read_nocopy(cur, len * T::FILE_SIZE)?,
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
    JniGlobal(GcRootJniGlobal<T>),
    JniLocal(GcRootJniLocal<T>),
    JavaFrame(GcRootJavaFrame<T>),
    NativeStack(GcRootNativeStack<T>),
    StickyClass(GcRootStickyClass<T>),
    ThreadBlock(GcRootThreadBlock<T>),
    MonitorUsed(GcRootMonitorUsed<T>),
    ThreadObj(GcRootThreadObj<T>),
}

impl<T: Id> GcRootData<T> {
    fn id(&self) -> T {
        match self {
            GcRootData::JniGlobal(x) => x.id,
            GcRootData::JniLocal(x) => x.id,
            GcRootData::JavaFrame(x) => x.id,
            GcRootData::NativeStack(x) => x.id,
            GcRootData::StickyClass(x) => x.id,
            GcRootData::ThreadBlock(x) => x.id,
            GcRootData::MonitorUsed(x) => x.id,
            GcRootData::ThreadObj(x) => x.id,
        }
    }
}

impl<'a, T: Id> HeapDumpEntry<'a, T> {
    pub fn read(record: &mut &'a [u8]) -> Result<HeapDumpEntry<'a, T>> {
        let tag = record.read_u8()?;

        let entry = match tag {
            GcRootJniGlobal::<T>::ID => HeapDumpEntry::RootJniGlobal(GcRootJniGlobal::read(record)?),
            GcRootJniLocal::<T>::ID => HeapDumpEntry::RootJniLocal(GcRootJniLocal::read(record)?),
            GcRootJavaFrame::<T>::ID => HeapDumpEntry::RootJavaFrame(GcRootJavaFrame::read(record)?),
            GcRootNativeStack::<T>::ID => HeapDumpEntry::RootNativeStack(GcRootNativeStack::read(record)?),
            GcRootStickyClass::<T>::ID => HeapDumpEntry::RootStickyClass(GcRootStickyClass::read(record)?),
            GcRootThreadBlock::<T>::ID => HeapDumpEntry::RootThreadBlock(GcRootThreadBlock::read(record)?),
            GcRootMonitorUsed::<T>::ID => HeapDumpEntry::RootMonitorUsed(GcRootMonitorUsed::read(record)?),
            GcRootThreadObj::<T>::ID => HeapDumpEntry::RootThreadObj(GcRootThreadObj::read(record)?),
            GcClassDump::<T>::ID => HeapDumpEntry::ClassDump(GcClassDump::read(record)?),
            GcInstanceDump::<T>::ID => HeapDumpEntry::InstanceDump(GcInstanceDump::read(record)?),
            GcObjArrayDump::<T>::ID => HeapDumpEntry::ObjArrayDump(GcObjArrayDump::read(record)?),
            GcPrimArrayDump::<T>::ID => HeapDumpEntry::PrimArrayDump(GcPrimArrayDump::read(record)?),

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
    EntityPlayerClass,
    CraftPlayerClass,
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
    b"java/lang/ref/Reference" => ClassNames::ReferenceClass,
    b"net/minecraft/server/level/EntityPlayer" => ClassNames::EntityPlayerClass,
    b"org/bukkit/craftbukkit/v1_20_R3/entity/CraftPlayer" => ClassNames::CraftPlayerClass
};

fn visit_prof<
    'a,
    T: Id,
    U: FnMut(T, &'a [u8]),
    V: FnMut(T, T),
    X: FnMut(GcRootData<T>),
    Y: FnMut(HeapDumpEntry<'a, T>) -> Result<()>,
>(
    mut file: &'a [u8],
    mut on_string: U,
    mut on_class: V,
    mut on_gc_root: X,
    mut on_heap_entry: Y,
) -> Result<()> {
    // Evict already-processed pages in 64 MiB chunks so the kernel can reclaim
    // them while the rest of the pass is still running.
    #[cfg(target_os = "linux")]
    let mmap_start = file.as_ptr();
    #[cfg(target_os = "linux")]
    let mut next_dontneed_at: usize = 64 << 20;

    while !file.is_empty() {
        #[cfg(target_os = "linux")]
        {
            let consumed = file.as_ptr() as usize - mmap_start as usize;
            if consumed >= next_dontneed_at {
                let evict_ptr = (mmap_start as usize + next_dontneed_at - (64 << 20)) as *mut libc::c_void;
                unsafe { libc::madvise(evict_ptr, 64 << 20, libc::MADV_DONTNEED); }
                next_dontneed_at += 64 << 20;
            }
        }

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
                        HeapDumpEntry::RootJniGlobal(root) => on_gc_root(GcRootData::JniGlobal(root)),
                        HeapDumpEntry::RootJniLocal(root) => on_gc_root(GcRootData::JniLocal(root)),
                        HeapDumpEntry::RootJavaFrame(root) => on_gc_root(GcRootData::JavaFrame(root)),
                        HeapDumpEntry::RootNativeStack(root) => on_gc_root(GcRootData::NativeStack(root)),
                        HeapDumpEntry::RootStickyClass(root) => on_gc_root(GcRootData::StickyClass(root)),
                        HeapDumpEntry::RootThreadBlock(root) => on_gc_root(GcRootData::ThreadBlock(root)),
                        HeapDumpEntry::RootMonitorUsed(root) => on_gc_root(GcRootData::MonitorUsed(root)),
                        HeapDumpEntry::RootThreadObj(root) => on_gc_root(GcRootData::ThreadObj(root)),
                        x => on_heap_entry(x)?,
                    }
                }
            }
            _ => {}
        }
    }

    Ok(())
}


fn madvise(file: &[u8], sequential: bool) {
    #[cfg(target_os = "linux")]
    unsafe {
        let advice = if sequential { libc::MADV_SEQUENTIAL } else { libc::MADV_DONTNEED };
        libc::madvise(file.as_ptr() as *mut libc::c_void, file.len(), advice);
    }
}

fn do_read_prof<'a, T: Id>(file: &'a [u8], min_leaked: usize, min_pattern_leaked: usize, normalize_inner_classes: bool, show_ids: bool, json: bool) -> Result<bool> {
    use ClassNames::*;

    let str_dict = RefCell::new(IntMap::default());
    let mut classes = IntMap::default();
    let mut class_names = IntMap::default();
    let mut gc_roots: IntMap<_, SmallVec<[GcRootData<T>; 2]>> = IntMap::default();

    let mut edges: Vec<(T, T)> = Vec::new();
    let mut world_server_instances = Vec::new();
    let mut entity_player_instances = Vec::new();
    let mut craft_player_instances = Vec::new();

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

    // Returns T::NULL (0) when a special class wasn't found in the heap dump, which makes every
    // comparison against it false — effectively disabling that detection path gracefully.
    let get_class_id = |id: ClassNames| class_ids[id as usize].get().copied().unwrap_or(T::NULL);

    eprintln!("parsing heap dump");

    madvise(file, true);

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
                if v.get().map_or(false, |s| name_id == *s) {
                    let res = class_ids[idx].set(obj_id);
                    debug_assert!(res.is_ok());
                }
            }
        },
        |root: GcRootData<T>| {
            gc_roots.entry(root.id()).or_insert(SmallVec::new()).push(root);
        },
        |entry| {
            match entry {
                HeapDumpEntry::ClassDump(class) => {
                    for (_name_id, static_value) in &class.statics {
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
                    } else if inst.class_id == get_class_id(EntityPlayerClass) {
                        entity_player_instances.push(inst.id);
                    } else if inst.class_id == get_class_id(CraftPlayerClass) {
                        craft_player_instances.push(inst.id);
                    } else if inst.class_id == get_class_id(DedicatedServerClass) {
                        class.iter_fields(inst.data, &classes, |_, name_id, value| {
                            if str_dict.borrow()[&name_id] == b"Q"
                                && let JVMValue::Obj(child) = value
                            {
                                non_leak_root_sources.push(child);
                                eprintln!("found non-leak root: DedicatedServer#levels: {child:x}");
                            }
                        })?;
                    } else if inst.class_id == get_class_id(CraftServerClass) {
                        class.iter_fields(inst.data, &classes, |_, name_id, value| {
                            if str_dict.borrow()[&name_id] == b"worlds"
                                && let JVMValue::Obj(child) = value
                            {
                                non_leak_root_sources.push(child);
                                eprintln!("found non-leak root: CraftServer#worlds: {child:x}");
                            }
                        })?;
                    } else if inst.class_id == get_class_id(CraftSchedulerClass)
                        || inst.class_id == get_class_id(CraftAsyncSchedulerClass)
                    {
                        eprintln!("found scheduler instance: {:x}", inst.id);
                        leak_root_sources.push(inst.id);
                    }

                    class.iter_fields(inst.data, &classes, |cl_id, _name_id, value| {
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
                    let len = arr.data.len() / T::FILE_SIZE;
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

    // Warn when detection-critical classes were not found. This usually means the hardcoded
    // class name mappings (currently targeting v1_20_R3) are out of date for the Minecraft
    // version that produced this heap dump.
    let scheduler_found = class_ids[CraftSchedulerClass as usize].get().is_some()
        || class_ids[CraftAsyncSchedulerClass as usize].get().is_some();
    let leak_targets_found = class_ids[WorldServerClass as usize].get().is_some()
        || class_ids[EntityPlayerClass as usize].get().is_some()
        || class_ids[CraftPlayerClass as usize].get().is_some();
    if !scheduler_found {
        eprintln!(
            "warning: neither CraftScheduler nor CraftAsyncScheduler was found in the heap dump"
        );
        eprintln!(
            "         no leak root sources can be identified — all paths-to-root will be empty"
        );
        eprintln!("         the class name mappings may be out of date (currently target v1_20_R3)");
    }
    if !leak_targets_found {
        eprintln!(
            "warning: no leak target classes (WorldServer, EntityPlayer, CraftPlayer) were found"
        );
        eprintln!("         the class name mappings may be out of date (currently target v1_20_R3)");
    }

    eprintln!("clean graph");

    clean_graph(&mut edges);

    // Combine all leak target classes into one pool for unified analysis.
    let all_leak_target_instances: Vec<T> = world_server_instances
        .iter()
        .chain(entity_player_instances.iter())
        .chain(craft_player_instances.iter())
        .copied()
        .collect();

    // Fast membership test used during path trimming below.
    let all_leak_target_set: IntSet<T> = all_leak_target_instances.iter().copied().collect();

    eprintln!("finding paths to root");
    eprintln!("found {} total leak target instances", all_leak_target_instances.len());

    let globally_reachable =
        is_reachable(&edges, |f| gc_roots.contains_key(&f), &all_leak_target_instances);
    let non_leaked_instances =
        is_reachable(&edges, |f| non_leak_root_sources.contains(&f), &all_leak_target_instances);

    let mut candidates: Vec<T> = Vec::new();
    for (inst, global, non_leak) in izip!(
        all_leak_target_instances.iter(),
        globally_reachable.iter(),
        non_leaked_instances.iter()
    ) {
        if *global && !*non_leak {
            candidates.push(*inst);
        }
    }

    eprintln!("found {} likely leak candidates", candidates.len());

    if candidates.len() < min_leaked {
        return Ok(false);
    }

    eprintln!("finding leaked instance paths-to-root");

    let candidate_paths: Vec<Vec<T>> = candidates
        .iter()
        .map(|&c| find_shortest_path(&edges, |f| leak_root_sources.contains(&f), c))
        .collect();

    // Build the small sets needed to collect field names in pass 2.
    // Only edges that appear in candidate paths require a field name annotation.
    let mut needed_field_edges: IntSet<(T, T)> = IntSet::default();
    let mut needed_parent_set: IntSet<T> = IntSet::default();
    for path in &candidate_paths {
        for w in path.windows(2) {
            needed_field_edges.insert((w[0], w[1]));
            needed_parent_set.insert(w[1]);
        }
    }

    // Class static field names can be resolved from the already-in-memory `classes` map.
    let mut edge_field_names: IntMap<(T, T), T> = IntMap::default();
    for (_, class) in &classes {
        for (name_id, static_value) in &class.statics {
            if let JVMValue::Obj(child) = static_value {
                let edge = (*child, class.id);
                if needed_field_edges.contains(&edge) {
                    edge_field_names.entry(edge).or_insert(*name_id);
                }
            }
        }
    }

    eprintln!("re-gathering instance data");

    drop(edges);

    // Release page cache for the mmap before re-reading so it doesn't compete
    // with the in-memory data structures for RAM.
    madvise(file, false);
    madvise(file, true);

    let mut relevant_inst: IntSet<T> = IntSet::default();
    let mut inst_data: IntMap<T, HeapDumpEntry<'a, T>> = IntMap::default();
    relevant_inst.extend(candidate_paths.iter().flatten().copied());

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
                    // While we have the instance data in hand, collect field names for
                    // any candidate-path edges where this instance is the parent.
                    if needed_parent_set.contains(&inst.id) {
                        let class = classes.get(&inst.class_id).unwrap();
                        class.iter_fields(inst.data, &classes, |cl_id, name_id, value| {
                            if cl_id == get_class_id(ReferenceClass) { return; }
                            if let JVMValue::Obj(child) = value {
                                let edge = (child, inst.id);
                                if needed_field_edges.contains(&edge) {
                                    edge_field_names.entry(edge).or_insert(name_id);
                                }
                            }
                        })?;
                    }
                    on_data(inst.id, HeapDumpEntry::InstanceDump(inst))
                }
                HeapDumpEntry::ObjArrayDump(inst) => on_data(inst.id, HeapDumpEntry::ObjArrayDump(inst)),
                _ => {}
            }
            Ok(())
        },
    )?;

    // Group paths by class-name signature, deduplicating across all candidate types.
    // Each path is trimmed to start at the last (nearest-to-scheduler) leak target
    // in the path: a WorldServer leaked only because a CraftPlayer is leaked folds
    // into the CraftPlayer's pattern rather than creating a redundant WorldServer entry.
    let mut pattern_order: Vec<Vec<String>> = Vec::new();
    let mut pattern_terminals: IntMap<Vec<String>, IntSet<T>> = IntMap::default();
    let mut pattern_example: IntMap<Vec<String>, Vec<(T, String, Option<String>)>> = IntMap::default();
    let mut pattern_example_score: IntMap<Vec<String>, usize> = IntMap::default();

    for (path, &candidate) in izip!(candidate_paths.iter(), candidates.iter()) {
        if path.is_empty() {
            let sig = vec!["<no path found>".to_string()];
            let is_new = !pattern_terminals.contains_key(&sig);
            pattern_terminals.entry(sig.clone()).or_default().insert(candidate);
            if is_new {
                pattern_order.push(sig.clone());
                pattern_example.insert(sig, vec![]);
            }
            continue;
        }

        // Trim the path to start at the last leak target class encountered walking
        // from the candidate toward the scheduler root. This collapses e.g.
        // [WorldServer, EntityPlayer, CraftPlayer, HashMap, ..., CraftScheduler]
        // into [CraftPlayer, HashMap, ..., CraftScheduler], attributing the leak
        // to the innermost retained object rather than its transitive dependents.
        let trimmed_start = path
            .iter()
            .rposition(|id| all_leak_target_set.contains(id))
            .unwrap_or(0);
        let trimmed = &path[trimmed_start..];
        let terminal = trimmed[0];

        // Resolve class names. Field annotations are collected separately so they
        // don't affect signature matching.
        let mut raw: Vec<(T, String)> = Vec::new();
        let mut field_annotations: Vec<Option<String>> = Vec::new();
        for (i, ele) in trimmed.iter().enumerate() {
            let name: String = match inst_data.get(ele) {
                Some(HeapDumpEntry::InstanceDump(inst)) => {
                    let class = classes.get(&inst.class_id).unwrap();
                    let class_name_id = class_names.get(&class.id).unwrap();
                    let dict = str_dict.borrow();
                    let class_name = dict.get(class_name_id).unwrap();
                    str::from_utf8(class_name)?.to_string()
                }
                Some(HeapDumpEntry::ObjArrayDump(inst)) => {
                    let class = classes.get(&inst.class_id).unwrap();
                    let class_name_id = class_names.get(&class.id).unwrap();
                    let dict = str_dict.borrow();
                    let class_name_bytes = dict.get(class_name_id).unwrap();
                    let class_name = str::from_utf8(class_name_bytes)?;
                    // Simplify JVM array notation: [Ljava/lang/Object; -> java/lang/Object[]
                    if class_name.starts_with("[L") && class_name.ends_with(';') {
                        format!("{}[]", &class_name[2..class_name.len() - 1])
                    } else {
                        format!("{}[]", class_name)
                    }
                }
                None => {
                    let class = classes.get(ele).unwrap();
                    let class_name_id = class_names.get(&class.id).unwrap();
                    let dict = str_dict.borrow();
                    let class_name = dict.get(class_name_id).unwrap();
                    format!("Class<{}>", str::from_utf8(class_name)?)
                }
                _ => unreachable!(),
            };

            // Look up which field of trimmed[i] holds trimmed[i-1].
            let annotation = if i > 0 {
                let child = trimmed[i - 1];
                edge_field_names.get(&(child, *ele)).map(|&field_id| {
                    let dict = str_dict.borrow();
                    dict.get(&field_id)
                        .and_then(|b| str::from_utf8(b).ok())
                        .unwrap_or("?")
                        .to_string()
                })
            } else {
                None
            };

            raw.push((*ele, name));
            field_annotations.push(annotation);
        }

        // Signature: normalize inner class names (if enabled), then collapse
        // consecutive same-class runs. Normalization strips the $InnerClass suffix and
        // the Class<> wrapper so that e.g. HashMap$Node, HashMap$TreeNode,
        // BossAbilityGroup$1/$2, and Class<X>/X-instance pairs all map to the same sig.
        let mut sig: Vec<String> = Vec::new();
        for (_, name) in &raw {
            let norm = if normalize_inner_classes {
                normalize_class_name(name)
            } else {
                name.clone()
            };
            if sig.last().map_or(true, |last| last != &norm) {
                sig.push(norm);
            }
        }

        // Display path: collapsed runs (count not shown), field annotations, and in
        // normalize mode Class<X>+X instance pairs merged into one entry.
        let mut full_path: Vec<(T, String, Option<String>)> = Vec::new();
        let mut i = 0;
        while i < raw.len() {
            let name = raw[i].1.clone();
            let ele = raw[i].0;
            let annotation = field_annotations[i].clone();
            let mut run = 1;
            while i + run < raw.len() && raw[i + run].1 == name {
                run += 1;
            }
            i += run;
            // In normalize mode: collapse Class<X> + X instance into one entry.
            // The class-object entry carries the static field_name; the following
            // instance entry is only the class-pointer edge and carries no field name.
            let (class_name, field_name) = if normalize_inner_classes {
                if let Some(inner) = strip_class_wrapper(&name) {
                    if i < raw.len() && raw[i].1 == inner {
                        i += 1;
                        (inner.to_string(), annotation)
                    } else {
                        (name, annotation)
                    }
                } else {
                    (name, annotation)
                }
            } else {
                (name, annotation)
            };
            full_path.push((ele, class_name, field_name));
        }

        let annotation_score = field_annotations.iter().filter(|a| a.is_some()).count();

        let is_new = !pattern_terminals.contains_key(&sig);
        pattern_terminals.entry(sig.clone()).or_default().insert(terminal);
        if is_new {
            pattern_order.push(sig.clone());
            pattern_example_score.insert(sig.clone(), annotation_score);
            pattern_example.insert(sig, full_path);
        } else if annotation_score > pattern_example_score[&sig] {
            pattern_example_score.insert(sig.clone(), annotation_score);
            pattern_example.insert(sig, full_path);
        }
    }

    // Most-common patterns first.
    pattern_order.sort_by(|a, b| pattern_terminals[b].len().cmp(&pattern_terminals[a].len()));

    let suppressed = pattern_order
        .iter()
        .filter(|sig| pattern_terminals[*sig].len() < min_pattern_leaked)
        .count();
    let suppressed_note = if suppressed > 0 {
        format!(" ({} suppressed by --min-pattern-leaked)", suppressed)
    } else {
        String::new()
    };

    if json {
        // Summary goes to stderr so stdout is clean JSON.
        eprintln!(
            "=== {} leaked instance{}, {} unique retention pattern{}{} ===",
            candidates.len(),
            if candidates.len() == 1 { "" } else { "s" },
            pattern_order.len(),
            if pattern_order.len() == 1 { "" } else { "s" },
            suppressed_note,
        );
        let patterns: Vec<serde_json::Value> = pattern_order.iter()
            .filter(|sig| pattern_terminals[*sig].len() >= min_pattern_leaked)
            .map(|sig| {
                let count = pattern_terminals[sig].len();
                let chain: Vec<serde_json::Value> = pattern_example[sig].iter()
                    .map(|(_, class_name, field_name)| {
                        serde_json::json!({"class_name": class_name, "field_name": field_name})
                    })
                    .collect();
                serde_json::json!({"instance_count": count, "chain": chain})
            })
            .collect();
        println!("{}", serde_json::to_string(&patterns)?);
    } else {
        println!(
            "=== {} leaked instance{}, {} unique retention pattern{}{} ===\n",
            candidates.len(),
            if candidates.len() == 1 { "" } else { "s" },
            pattern_order.len(),
            if pattern_order.len() == 1 { "" } else { "s" },
            suppressed_note,
        );

        let mut display_index = 1usize;
        for sig in pattern_order.iter() {
            let terminals = &pattern_terminals[sig];
            if terminals.len() < min_pattern_leaked {
                continue;
            }
            let example_path = &pattern_example[sig];

            println!(
                "--- Pattern {} ({} instance{}) ---",
                display_index,
                terminals.len(),
                if terminals.len() == 1 { "" } else { "s" },
            );
            display_index += 1;

            if example_path.is_empty() {
                println!("  <no path found from scheduler>");
            } else {
                for (id, class_name, field_name) in example_path {
                    let display = if let Some(field) = field_name {
                        format!("{class_name}  (.{field})")
                    } else {
                        class_name.clone()
                    };
                    if show_ids {
                        println!("  {id:x} {display}");
                    } else {
                        println!("  {display}");
                    }
                }
            }
            println!();
        }
    }

    Ok(true)
}

const HEADER: &[u8; 19] = b"JAVA PROFILE 1.0.2\0";

pub fn read_prof(mut hprof_file: &[u8], min_leaked: usize, min_pattern_leaked: usize, normalize_inner_classes: bool, show_ids: bool, json: bool) -> Result<bool> {
    let mut header = [0; HEADER.len()];
    hprof_file.read_exact(&mut header)?;

    if *HEADER != header {
        return Err(anyhow!("bad header, expected {HEADER:?} but got {header:?}"));
    }

    let id_size = hprof_file.read_u32::<BigEndian>()?;
    let _micros = hprof_file.read_u64::<BigEndian>()?;

    if id_size == 4 {
        eprintln!("detected 4-byte object IDs (compressed OOPs)");
        do_read_prof::<u32>(hprof_file, min_leaked, min_pattern_leaked, normalize_inner_classes, show_ids, json)
    } else if id_size == 8 {
        // Shifted OOP values for heaps ≤ 32 GB fit in u32, halving edge memory.
        // Fall back to u64 only if a value overflows (heap > 32 GB).
        eprintln!("detected 8-byte object IDs (uncompressed OOPs); using compact u32 storage");
        do_read_prof::<OopId>(hprof_file, min_leaked, min_pattern_leaked, normalize_inner_classes, show_ids, json)
    } else {
        Err(anyhow!("illegal id_size: {id_size}"))
    }
}

fn strip_class_wrapper(name: &str) -> Option<&str> {
    if name.starts_with("Class<") && name.ends_with('>') {
        Some(&name[6..name.len() - 1])
    } else {
        None
    }
}

fn normalize_class_name(name: &str) -> String {
    // Strip Class<> wrapper so class objects group with their instances in the sig.
    let name = strip_class_wrapper(name).unwrap_or(name);
    // Strip inner class suffix (everything from the last '$' to the next ';', '>', or end).
    //   "org/foo/Bar$Inner"  -> "org/foo/Bar"
    //   "org/foo/Bar$1"      -> "org/foo/Bar"
    //   "java/lang/Object[]" -> "java/lang/Object[]"  (no '$', unchanged)
    if let Some(dollar) = name.rfind('$') {
        let mut result = name[..dollar].to_string();
        let rest = &name[dollar + 1..];
        let skip = rest.find([';', '>']).unwrap_or(rest.len());
        result.push_str(&rest[skip..]);
        result
    } else {
        name.to_string()
    }
}
