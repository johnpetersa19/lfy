conf_pkg = configuration_data()
conf_pkg.set('APP_ID', APP_ID)
conf_pkg.set('APP_NAME', meson.project_name())
conf_pkg.set('PACKAGE_URL', PACKAGE_URL)
conf_pkg.set('APP_DES', APP_DES)
conf_pkg.set('PACKAGE_URL_BUG', PACKAGE_URL_BUG)
conf_pkg.set('VERSION', meson.project_version())

subdir('deb/DEBIAN')
subdir('aur')
subdir('flatpak')
subdir('rpm/SPECS')
subdir('pip')

