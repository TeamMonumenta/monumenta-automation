use std::{
    fmt::{Debug, Display, LowerHex},
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
