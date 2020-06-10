;;; Directory Local Variables for emacs clang flycheck
;;; For more information see (info "(emacs) Directory Variables")

;;; Turn flycheck mode on for our c++ stuff and tell jedi where to look for our python stuff.
((c++-mode (eval . (flycheck-mode)))
 (python-mode (jedi:server-args . ("--sys-path" "__EFRO_PROJECT_ROOT__/tools"
                                   "--sys-path" "__EFRO_PROJECT_ROOT__/assets/src/ba_data/python")))
 ;; Shorter name in projectile status bar to save valuable space.
 (nil . ((projectile-project-name . "__EFRO_PROJECT_SHORTNAME__")))
 )
