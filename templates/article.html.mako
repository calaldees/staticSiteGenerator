<%include file="_head.mako"/>
<body>
<div id="layout" class="pure-g">
	<%include file="_nav.mako"/>

	<div class="content pure-u-1 pure-u-md-3-4">

		<div class="article_header">
			<h1>${title}</h1>
			<h2>${description}</h2>
		</div>
		<div class="article_content">
			${markdown_html}
		</div>

	</div>
</div>
</body>
</html>
