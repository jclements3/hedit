# vendor/

Third-party assets bundled into hedit.

## js-vim.min.js
- Source: https://github.com/itsjoesullivan/js-vim-embed (`vim.min.js`, the prebuilt
  browser bundle of https://github.com/itsjoesullivan/js-vim)
- A JavaScript implementation of the vim editor. © 2013 Joe Sullivan, **MIT Licensed**.
- Exposes a global `window.vim`; `vim.edit({el})` turns an element into a vim editor,
  `vim.curDoc.text()` gets/sets the buffer text, `vim.exec(keys)` runs commands.
- hedit loads it inside an **iframe** (see the `#vim-modal` / `VIM_SRCDOC` in `hedit.html`)
  so its document-wide key capture stays isolated from hedit's own shortcuts. Used for the
  "Edit JSON (vim)" source editor on the harp JSON.
