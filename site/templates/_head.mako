<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<%include file="_og_meta.mako"/>

	<title>${site.title} - ${title or ''}</title>
	<link id="favicon" rel="shortcut icon" type="image/svg" href="${site.favicon}" />

	<link rel="stylesheet" href="/static/pure-min.css">
	<link rel="stylesheet" href="/static/grids-responsive-min.css">
	<link rel="stylesheet" href="/static/pure-layout-blog.css"/>
	<%doc>
	<link rel="stylesheet" href="/static/pure-layout-side-menu.css"/>
	</%doc>

	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
	<%doc>
	<script type="module">
		import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
		mermaid.initialize({ startOnLoad: false })
		await mermaid.run({querySelector: '.language-mermaid'})
	</script>
	</%doc>

	<link rel="stylesheet" href="/static/page.css"/>
	<script src="/static/static_site.js" async></script>
	<%doc>
	<script src="https://pure-css.github.io/js/ui.js" async></script>
	</%doc>

	<link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml">
</head>
