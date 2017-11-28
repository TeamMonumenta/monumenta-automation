Insert these starting at line 1679 of `pymclevel/infiniteworld.py` to test 1.13 chunks
(I probably could have made a patch for this, but it's just for testing, not for actual use)

```
            # we're probably using a 1.13 file - save the chunk data for Tim's use
            with open('/home/tim/Desktop/chunk.nbt','wb') as f:
                f.write(data)
```

