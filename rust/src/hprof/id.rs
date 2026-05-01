use std::{
    fmt::{self, Debug, Display, LowerHex},
    hash::Hash,
    io::Error,
};

use byteorder::{BigEndian, ReadBytesExt};

pub trait Id: Sized + Hash + Copy + Eq + Display + LowerHex + Debug + Ord + Default {
    const NULL: Self;

    fn read_from(buf: &mut &[u8]) -> Result<Self, Error>;
}

impl Id for u32 {
    const NULL: Self = 0;

    fn read_from(buf: &mut &[u8]) -> Result<Self, Error> {
        buf.read_u32::<BigEndian>()
    }
}

impl Id for u64 {
    const NULL: Self = 0;

    fn read_from(buf: &mut &[u8]) -> Result<Self, Error> {
        let res = buf.read_u64::<BigEndian>()?;
        debug_assert!(res & 0b111 == 0);
        Ok(res >> 3)
    }
}

/// Reads 8-byte (uncompressed OOP) IDs from the HPROF file but stores them
/// as u32 after the standard >> 3 alignment shift.  Valid for heaps ≤ 32 GB,
/// where the shifted value never exceeds u32::MAX.  This halves edge-vector
/// memory compared to storing the same IDs as u64.
#[derive(Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Debug, Default)]
pub struct OopId(pub u32);

impl Display for OopId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        Display::fmt(&self.0, f)
    }
}

impl LowerHex for OopId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        LowerHex::fmt(&self.0, f)
    }
}

impl Id for OopId {
    const NULL: Self = OopId(0);

    fn read_from(buf: &mut &[u8]) -> Result<Self, Error> {
        let raw = buf.read_u64::<BigEndian>()?;
        debug_assert!(raw & 0b111 == 0, "unaligned OOP: {raw:#x}");
        let shifted = raw >> 3;
        debug_assert!(shifted <= u32::MAX as u64, "OOP exceeds u32 range (heap > 32 GB?): {shifted}");
        Ok(OopId(shifted as u32))
    }
}
