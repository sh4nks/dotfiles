;;----------------------------------------------------------------------------
;; Set load path
;;----------------------------------------------------------------------------
(eval-when-compile (require 'cl))
(if (fboundp 'normal-top-level-add-to-load-path)
    (let* ((my-lisp-dir "~/.emacs.d/site-lisp/")
           (default-directory my-lisp-dir))
      (progn
        (setq load-path
              (append
               (loop for dir in (directory-files my-lisp-dir)
                     unless (string-match "^\\." dir)
                     collecting (expand-file-name dir))
               load-path)))))

;;----------------------------------------------------------------------------
;; Ensure we're freshly byte-compiled
;;----------------------------------------------------------------------------
;(require 'bytecomp)
;(byte-recompile-directory "~/.emacs.d/site-lisp" 0)
;(byte-recompile-directory "~/.emacs.d/modules" 0)
;(byte-recompile-directory "~/.emacs.d/" 0)

;;----------------------------------------------------------------------------
;; Utilities for grabbing upstream libs
;;----------------------------------------------------------------------------
(defun site-lisp-dir-for (name)
  (expand-file-name (format "~/.emacs.d/site-lisp/%s" name)))

(defun site-lisp-library-el-path (name)
  (expand-file-name (format "%s.el" name) (site-lisp-dir-for name)))

(defun download-site-lisp-module (name url)
  (let ((dir (site-lisp-dir-for name)))
    (message "Downloading %s from %s" name url)
    (unless (file-directory-p dir)
      (make-directory dir)
      (add-to-list 'load-path dir))
    (let ((el-file (site-lisp-library-el-path name)))
      (url-copy-file url el-file t nil)
      el-file)))

(defun ensure-lib-from-url (name url)
  (unless (site-lisp-library-loadable-p name)
    (byte-compile-file (download-site-lisp-module name url))))

(defun site-lisp-library-loadable-p (name)
  "Return whether or not the library `name' can be loaded from a
source file under ~/.emacs.d/site-lisp/name/"
  (let ((f (locate-library (symbol-name name))))
    (and f (string-prefix-p (file-name-as-directory (site-lisp-dir-for name)) f))))

(defun ensure-lib-from-svn (name url)
  (let ((dir (site-lisp-dir-for name)))
    (unless (site-lisp-library-loadable-p name)
      (message "Checking out %s from svn" name)
      (save-excursion
        (shell-command (format "svn co %s %s" url dir) "*site-lisp-svn*"))
      (add-to-list 'load-path dir))))

;;----------------------------------------------------------------------------
;; Fix up some load paths for libs from git submodules
;;----------------------------------------------------------------------------
;(unless (file-directory-p (expand-file-name "~/.emacs.d/site-lisp/html5-el/relaxng"))
;  (error "Please run 'make relaxng' in site-lisp/html5-el"))

;(add-to-list 'load-path (expand-file-name "~/.emacs.d/site-lisp/session/lisp"))
;(add-to-list 'load-path (expand-file-name "~/.emacs.d/site-lisp/org-mode/lisp"))
;(add-to-list 'load-path (expand-file-name "~/.emacs.d/site-lisp/org-mode/contrib/lisp"))

;(defun refresh-site-lisp-submodules ()
;  (interactive)
;  (message "Updating site-lisp git submodules")
;  (shell-command "cd ~/.emacs.d && git submodule foreach 'git pull' &" "*site-lisp-submodules*"))

;;----------------------------------------------------------------------------
;; Download these upstream libs
;;----------------------------------------------------------------------------
(defun remove-site-lisp-libs ()
  (shell-command "cd ~/.emacs.d && grep -e '^site-lisp/' .gitignore|xargs rm -rf"))

(defun ensure-site-lisp-libs ()
  (unless (> emacs-major-version 23)
    (ensure-lib-from-url 'package "http://bit.ly/pkg-el23")))

(defun refresh-site-lisp ()
  (interactive)
  (refresh-site-lisp-submodules)
  (remove-site-lisp-libs)
  (ensure-site-lisp-libs))

(ensure-site-lisp-libs)

;;------------------------------------------------------------------------------
;; Load the package.el
;;------------------------------------------------------------------------------
(require 'package)

;;------------------------------------------------------------------------------
;; Patch up annoying package.el quirks
;;------------------------------------------------------------------------------
(defadvice package-generate-autoloads (after close-autoloads (name pkg-dir) activate)
  "Stop package.el from leaving open autoload files lying around."
  (let ((path (expand-file-name (concat name "-autoloads.el") pkg-dir)))
    (with-current-buffer (find-file-existing path)
      (kill-buffer nil))))

;;------------------------------------------------------------------------------
;; Add support to package.el for pre-filtering available packages
;;------------------------------------------------------------------------------
(defvar package-filter-function nil
  "Optional predicate function used to internally filter packages used by package.el.

The function is called with the arguments PACKAGE VERSION ARCHIVE, where
PACKAGE is a symbol, VERSION is a vector as produced by `version-to-list', and
ARCHIVE is the string name of the package archive.")

(defadvice package--add-to-archive-contents
  (around filter-packages (package archive) activate)
  "Add filtering of available packages using `package-filter-function', if non-nil."
  (when (or (null package-filter-function)
            (funcall package-filter-function
                     (car package)
                     (package-desc-vers (cdr package))
                     archive))
    ad-do-it))

;;------------------------------------------------------------------------------
;; On-demand installation of packages
;;------------------------------------------------------------------------------
(defun require-package (package &optional min-version no-refresh)
  "Ask elpa to install given PACKAGE."
  (if (package-installed-p package min-version)
      t
    (if (or (assoc package package-archive-contents) no-refresh)
        (package-install package)
      (progn
        (package-refresh-contents)
        (require-package package min-version t)))))

;;------------------------------------------------------------------------------
;; Standard package repositories
;;------------------------------------------------------------------------------
(add-to-list 'package-archives '("marmalade" . "http://marmalade-repo.org/packages/"))

;;------------------------------------------------------------------------------
;; Also use Melpa for some packages built straight from VC
;;------------------------------------------------------------------------------
(add-to-list 'package-archives '("melpa" . "http://melpa.milkbox.net/packages/"))

(defvar melpa-exclude-packages
  '(slime)
  "Don't install Melpa versions of these packages.")

;; Don't take Melpa versions of certain packages
(setq package-filter-function
      (lambda (package version archive)
        (or (not (string-equal archive "melpa"))
            (not (memq package melpa-exclude-packages)))))

;;------------------------------------------------------------------------------
;; Fire up package.el and ensure the following packages are installed.
;;------------------------------------------------------------------------------
(package-initialize)

;; Misc
(require-package 'ido-ubiquitous)
(require-package 'eldoc-eval)
(require-package 'smex)
(require-package 'dired+)
(require-package 'autopair)
(require-package 'marmalade)
(require-package 'ibuffer-vc)
(require-package 'auto-complete)
(require-package 'flymake-cursor)
(require-package 'fringe-helper)
(require-package 'flymake-haml)
(require-package 'flymake-python-pyflakes)
(require-package 'flymake-sass)
(require-package 'flymake-shell)

;; YAML-Mode
(require-package 'yaml-mode)

;; HTML
;(require-package 'htmlize)

;; CSS-Mode
(require-package 'mmm-mode)
(require-package 'rainbow-mode)
(require-package 'less-css-mode)
(require-package 'flymake-css)
(require-package 'tidy)

;; Javascript-Mode
(require-package 'js-comint)
(require-package 'json)
(require-package 'js3-mode)
(require-package 'js2-mode)
(require-package 'flymake-jslint)

;; Lua-Mode
(require-package 'lua-mode)

(provide 'packages)
