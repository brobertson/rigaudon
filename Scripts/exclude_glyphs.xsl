<xsl:stylesheet version="2.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:param name="glyph_name" select="'greek.capital.letter.pi'"/>
<xsl:template match="glyph[ contains(ids/id/@name, $glyph_name) ]"><!--/id/@name='latin.small.letter.a']"-->
 <xsl:comment>Removed element <xsl:value-of select="$glyph_name"/>
 </xsl:comment>
</xsl:template>

<xsl:template match="@*|node()">
	<xsl:copy>
		<xsl:apply-templates select="@*|node()"/>
	</xsl:copy>
</xsl:template>
</xsl:stylesheet>
