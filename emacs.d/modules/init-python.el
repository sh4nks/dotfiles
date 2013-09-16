(defun customizations-for-python-mode ()
  (interactive)
  (auto-complete-mode)
  ;(setq whitespace-line-column 80)
)

;;----------------------------------------------------------------------------
;; On-the-fly syntax checking via flymake
;;----------------------------------------------------------------------------
(eval-after-load 'python
  '(require 'flymake-python-pyflakes))

(add-hook 'python-mode-hook 'customizations-for-python-mode 'flymake-python-pyflakes-load)


(provide 'init-python)
