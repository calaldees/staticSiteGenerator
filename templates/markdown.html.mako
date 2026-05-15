<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<%include file="_og_meta.mako"/>

	<title>${metadata.title}</title>
	<link id="favicon" rel="shortcut icon" type="image/png" href="data:image/png;base64,....==" />

	<!-- Styles -->
	<link rel="stylesheet" href="static/pure-min.css">
	<link rel="stylesheet" href="static/grids-responsive-min.css">
	<link rel="stylesheet" href="static/page.css"/>
	<%doc>
	<style>
	<%include file="pure-min.css"/>
	<%include file="grids-responsive-min.css"/>
	<%include file="pure-layout-marketing.css"/>
	<%include file="page.css"/>
	</style>
	</%doc>

	<!-- Scripts -->
	<script src="/static/static_site.js" async></script>

	<!-- CDN -->
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
	<script type="module">
		import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
		mermaid.initialize({ startOnLoad: false })
		await mermaid.run({
			querySelector: '.language-mermaid',
		})
	</script>
	<!--
	<script src="https://cdn.jsdelivr.net/npm/@mermaid-js/tiny@11/dist/mermaid.tiny.js" async></script>
	-->
</head>
<body>

<h1>${metadata.title}</h1>

${markdown_html}

</body>
</html>
