<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:cb="http://www.cbwiki.net/wiki/index.php/Specification_1.2/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <xsl:output indent="yes"/>
  <xsl:strip-space elements="*"/>
  
<xsl:template match="/">
    <Candidats>
      <xsl:apply-templates select="descendant::channel/item"/>
    </Candidats>
  </xsl:template>
  
  <xsl:template match="cb:interestRate">
    <xsl:copy>
      <xsl:copy-of select="cb:rateName"/>
      <xsl:copy-of select="cb:rateType"/>
      <xsl:copy-of select="cb:observation/cb:value"/>
      <xsl:copy-of select="ancestor::channel/item/dc:date"/>
      <xsl:copy-of select="cb:observation/cb:unit"/>
      <xsl:copy-of select="cb:observation/cb:decimals"/>
      <xsl:copy-of select="cb:observationPeriod/cb:frequency"/>
      <xsl:copy-of select="cb:observationPeriod/cb:period"/>
    </xsl:copy>
  </xsl:template>

  
</xsl:stylesheet>