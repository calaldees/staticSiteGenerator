CDN_PURE:='https://cdn.jsdelivr.net/npm/purecss@3.0.0/build'

pure: pure-min.css pure-layout-blog.css grids-responsive-min.css pure-layout-blog.css
pure-min.css:
	curl ${CDN_PURE}/$@ -o $@
grids-responsive-min.css:
	curl ${CDN_PURE}/$@ -o $@

pure-layout-blog.css:
	curl https://pure-css.github.io/layouts/blog/styles.css -o $@
pure-layout-marketing.css:
	curl https://pure-css.github.io/layouts/marketing/styles.css -o $@
pure-layout-side-menu.css:
	curl https://pure-css.github.io/layouts/side-menu/styles.css -o $@
