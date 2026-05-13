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

	<!-- CDN -->
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
</head>
<body>

<h1>Static Site Generator</h1>

${markdown_html}

</body>
</html>
