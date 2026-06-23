<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<%include file="_og_meta.mako"/>

	<title>${site.title}${f' - {title}' if title else ''}</title>
	<link id="favicon" rel="shortcut icon" type="image/svg" href="${site.logo}" />

	<link rel="stylesheet" href="/static/css/pure-min.css">
	<link rel="stylesheet" href="/static/css/grids-responsive-min.css">
	<%doc>
	<link rel="stylesheet" href="/static/css/pure-layout-blog.css"/>
	<link rel="stylesheet" href="/static/css/pure-layout-side-menu.css"/>
	</%doc>

	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
	<%doc>
	<script type="module">
		import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
		mermaid.initialize({ startOnLoad: false })
		await mermaid.run({querySelector: '.language-mermaid'})
	</script>
	</%doc>

	<link rel="stylesheet" href="/static/css/page.css"/>
	<script src="/static/js/static_site.js" async></script>
	<%doc>
	<script src="https://pure-css.github.io/js/ui.js" async></script>
	</%doc>

	<%include file="_json-ld.mako"/>

	<link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml">
</head>
