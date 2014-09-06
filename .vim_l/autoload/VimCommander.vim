
function! VimCommander#UpdateMarks()
    call MarkStack#UpdateMarksInDirectory(Ave#ProjectRoot#GetDir(), '\.py$')
endfunction

