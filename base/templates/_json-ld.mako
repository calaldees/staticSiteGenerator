<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        "@id": "${site.url}/#website",
        "url": "${site.url}",
        "name": "${site.title}",
        "description": "{site.tagline}"
        "inLanguage": "${site.language or 'en'}",
      },
      "publisher": {
        "@id": "${site.url}/#person"
      },
      "image": {
        "@type": "ImageObject",
        "@id": "${site.url}/#website-image",
        "url": "${site.url}/${site.logo}",
        "caption": "${site.title} Logo"
      }
    ]
  }
</script>