# safe-copy
## Summary
Python util to safely copy a folder from source to destination, in a way that the destination can be validated

I've created this small app as I wanted to guarantee the integrity of copying larger files over my network to my NAS, 
as well as being able to later validate the integrity of this data remains unchanged.

## Commands
### safe-copy
The main utility is the `safe-copy` util itself, which takes s source and destination directory, copies the contents, and 
then verifies that the destination files are valid (as determined via their checksums)

Example:<br/><br/>
`safe-copy /media/data /mnt/backup`<br/>
<br/>
This will copy the contents `/media/data` into `/mnt/backup` (with the directory  `/mnt/backup/data` being created), 
after validating all files at the destination are the same it will write the checksums to `/mnt/backup/data/sum.txt`

### safe-validate
This is the companion utility to `safe-copy`, `safe-validate` will look at a directory that has previously been copied
and validate its contents against the `sum.txt` on disk.

Example:<br/><br/>
`safe-validate /mnt/backup/data`
<br/>
This will compare the checksums stored in `/mnt/backup/data/sum.txt` against the contents of `/mnt/backup/data/`. 

## Future Work
For the moment I'm happy with the functionality of these utilities (as they give me what I need at the moment), however
if I have more time to spend I would like to add the following:
* Improve the way the file stats are stored (its quite messy/inefficient to have to recurse over the whole array when
trying to find a specific file details).
* Make safe-copy aware of when the destination already contains a `sum.txt` and merge the contents (be aware of new files, 
missing files, and changed files)
* Make safe-validate recursive. At the moment it assumes the directory passed in contains the `sum.txt` file, however it 
would be great for future if you could point it at a root directory and it recurses the directory tree and validates any
directory it finds that has a checksums file.