(autoload 'pkgbuild-mode "pkgbuild-mode.el" "PKGBUILD Mode." t)
(setq auto-mode-alist (append '(("/PKGBUILD$" . pkgbuild-mode))
                              auto-mode-alist))

(provide 'init-pkgbuild)
