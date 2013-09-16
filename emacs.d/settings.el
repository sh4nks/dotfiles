;; Don't display the 'Welcome to GNU Emacs' buffer on startup
(setq inhibit-startup-message t)

;; Don't insert instructions in the *scratch* buffer
(setq initial-scratch-message nil)

;; Disable menu bar
(menu-bar-mode -1)

;; Use the system default monospaced font in Gnome
(setq font-use-system-font t)
(setq global-font-lock-mode t)

;; disable backup
(setq backup-inhibited t)

;; Make "yes or no" to "y or n"
(fset 'yes-or-no-p 'y-or-n-p)

;; Display the line and column number in the modeline
(setq line-number-mode t)
(setq column-number-mode t)

;; Highlight matching parentheses when the point is on them.
(show-paren-mode 1)
(set-default 'indicate-empty-lines t)

;; Set the highlight current line minor mode
;;(global-hl-line-mode t)

;; Use spaces, not tabs
(setq-default indent-tabs-mode nil)

;; Use 4 spaces
(setq default-tab-width 4)
(setq tab-width 4)

;; Don't disable narrowing commands
(put 'narrow-to-region 'disabled nil)
(put 'narrow-to-page 'disabled nil)
(put 'narrow-to-defun 'disabled nil)

;; Autopair quotes and parentheses
(require 'autopair)
(setq autopair-autowrap t)
(autopair-global-mode t)

;; Auto Indentation with enter
(define-key global-map (kbd "RET") 'newline-and-indent)

;; ido mode
(smex-initialize)
(ido-mode t)
(ido-ubiquitous t)
(setq ido-enable-prefix nil
      ido-enable-flex-matching t
      ido-auto-merge-work-directories-length nil
      ido-create-new-buffer 'always
      ido-use-filename-at-point 'guess
      ido-use-virtual-buffers t
      ido-handle-duplicate-virtual-buffers 2
      ido-max-prospects 10)


;; Remove trailing whitespace on save
(add-hook 'before-save-hook 'delete-trailing-whitespace)

;; More powerful tab-completion
(add-hook 'minibuffer-setup-hook
    '(lambda ()
    (define-key minibuffer-local-map "\t" 'comint-dynamic-complete)))


;; Exec Path
(when (memq window-system '(mac ns))
  (exec-path-from-shell-initialize))


;; IBuffer
(add-hook 'ibuffer-hook 'ibuffer-set-up-preferred-filters)
(eval-after-load 'ibuffer
  '(progn
     ;; Use human readable Size column instead of original one
     (define-ibuffer-column size-h
       (:name "Size" :inline t)
       (cond
        ((> (buffer-size) 1000000) (format "%7.1fM" (/ (buffer-size) 1000000.0)))
        ((> (buffer-size) 1000) (format "%7.1fk" (/ (buffer-size) 1000.0)))
        (t (format "%8d" (buffer-size)))))))

;; Explicitly require ibuffer-vc to get its column definitions, which
;; can't be autoloaded
(eval-after-load 'ibuffer
  '(require 'ibuffer-vc))

;; Modify the default ibuffer-formats
(setq ibuffer-formats
      '((mark modified read-only vc-status-mini " "
              (name 18 18 :left :elide)
              " "
              (size-h 9 -1 :right)
              " "
              (mode 16 16 :left :elide)
              " "
              (vc-status 16 16 :left)
              " "
              filename-and-process)))

(setq ibuffer-filter-group-name-face 'font-lock-doc-face)


;; Dired
(eval-after-load 'dired
  '(progn
     (require 'dired+)
     (setq dired-recursive-deletes 'top)
     (define-key dired-mode-map [mouse-2] 'dired-find-file)))

(provide 'settings)
