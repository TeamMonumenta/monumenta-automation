use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::atomic::{AtomicUsize, Ordering};

struct TrackingAlloc;

static CURRENT: AtomicUsize = AtomicUsize::new(0);
static PEAK: AtomicUsize = AtomicUsize::new(0);

unsafe impl GlobalAlloc for TrackingAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let size = layout.size();
        let ptr = unsafe { System.alloc(layout) };

        if !ptr.is_null() {
            let new = CURRENT.fetch_add(size, Ordering::SeqCst) + size;
            PEAK.fetch_max(new, Ordering::SeqCst);
        }

        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        let size = layout.size();
        CURRENT.fetch_sub(size, Ordering::SeqCst);
        unsafe { System.dealloc(ptr, layout) };
    }

    unsafe fn realloc(&self, ptr: *mut u8, old_layout: Layout, new_size: usize) -> *mut u8 {
        let old_size = old_layout.size();

        let new_ptr = unsafe { System.realloc(ptr, old_layout, new_size) };

        if !new_ptr.is_null() {
            if new_size > old_size {
                let delta = new_size - old_size;
                let new = CURRENT.fetch_add(delta, Ordering::SeqCst) + delta;
                PEAK.fetch_max(new, Ordering::SeqCst);
            } else {
                let delta = old_size - new_size;
                CURRENT.fetch_sub(delta, Ordering::SeqCst);
            }
        }

        new_ptr
    }
}

#[global_allocator]
static A: TrackingAlloc = TrackingAlloc;

pub fn current_usage() -> usize {
    CURRENT.load(Ordering::SeqCst)
}

pub fn peak_usage() -> usize {
    PEAK.load(Ordering::SeqCst)
}
