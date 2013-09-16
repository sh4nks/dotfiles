;;----------------------------------------------------------------------------
;; Rearrange split windows
;;----------------------------------------------------------------------------
(global-set-key "\C-x|" 'split-window-horizontally-instead)
(global-set-key "\C-x_" 'split-window-vertically-instead)


;;----------------------------------------------------------------------------
;; Custom Keybindings
;;----------------------------------------------------------------------------
(global-set-key (kbd "C-x C-m") 'execute-extended-command)
(global-set-key (kbd "C-c p") 'duplicate-line)

;; Kill buffer
(global-set-key (kbd "C-c C-k") 'kill-other-buffer)

(global-set-key [C-tab] 'other-window)

;; Get a buffer menu with the right mouse button.
(global-set-key [mouse-3] 'mouse-buffer-menu)

;; F6 stores a position in a file, F7 brings you back to this position
(global-set-key [f6] '(lambda () (interactive) (point-to-register ?1)))
(global-set-key [f7] '(lambda () (interactive) (register-to-point ?1)))

;; C-k is kill-whole-line
(global-set-key "\C-k" 'kill-whole-line)

;;ido completion in M-x
(global-set-key "\M-x" 'smex)

(global-set-key (kbd "C-x C-b") 'ibuffer)
(global-set-key [(meta f12)] 'magit-status)
(global-set-key [(shift meta f12)] 'magit-status-somedir)

(provide 'bindings)
