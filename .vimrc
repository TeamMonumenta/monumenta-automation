" Remove whitespace from end of lines when saving
autocmd BufWritePre * :%s/\s\+$//e

"set errorformat=%W%f:%l:\ warning:\ %m,%E%f:%l:\ error:\ %m,%+C%[\ %\\t]%.%#
set makeprg=pylint\ %
