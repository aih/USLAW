<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:html="http://www.w3.org/1999/xhtml" version="1.0"
                exclude-result-prefixes="html">
  <xsl:output method="html" indent="yes" encoding="UTF-8" />
  <xsl:template match="/">
    <html>
      <head>
        <title>
          <xsl:value-of select="//SUBJECT" /> 
        </title>
      </head>
      <body>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
