<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<%include file="_og_meta.mako"/>

	<title>${metadata.title}</title>
	<link id="favicon" rel="shortcut icon" type="image/png" href="data:image/png;base64,....==" />

	<link rel="stylesheet" href="/static/pure-min.css">
	<link rel="stylesheet" href="/static/grids-responsive-min.css">
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
	<script type="module">
		import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
		mermaid.initialize({ startOnLoad: false })
		await mermaid.run({querySelector: '.language-mermaid'})
	</script>

	<link rel="stylesheet" href="/static/page.css"/>
	<script src="/static/static_site.js" async></script>
</head>
<body>

<div id="main">
	<div class="header">
		<h1>${metadata.title}</h1>
		<h2>${metadata.description}</h2>
	</div>
	<div class="content">${markdown_html}</div>
</div>

</body>
</html>
