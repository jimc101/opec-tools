<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html"
                version="1.0"
                encoding="ISO-8859-1"
                omit-xml-declaration="yes"
                standalone="yes"
                doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
                doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
                cdata-section-elements="value"
                indent="yes"
                media-type="text/html"/>

    <xsl:template match="/">

        <html>
            <head>
                <title>Match-up Analysis</title>
                <link rel="stylesheet" type="text/css" href="styleset.css"/>
            </head>
            <body>

                <h2>Match-up Analysis Report</h2>

                <h3>Processing Information</h3>

                <table>
                    <tr>
                        <td class="name">Performed at:</td>
                        <td class="value">
                            <xsl:value-of select="analysisSummary/performedAt"/>
                        </td>
                    </tr>
                    <tr>
                        <td class="name">Number of match-ups:</td>
                        <td class="value">
                            <xsl:value-of select="analysisSummary/recordCount"/>
                        </td>
                    </tr>
                    <tr>
                        <td class="name">Model variable:</td>
                        <td class="value">
                            <xsl:value-of select="analysisSummary/modelVariable"/>
                        </td>
                    </tr>
                    <tr>
                        <td class="name">Reference variable:</td>
                        <td class="value">
                            <xsl:value-of select="analysisSummary/referenceVariable"/>
                        </td>
                    </tr>
                </table>

                <h3>Analysis Configuration</h3>

                <table>
                    <tr class="table_header">
                        <td>
                            Parameter
                        </td>
                        <td>
                            Value
                        </td>
                        <td>
                            Unit
                        </td>
                    </tr>
                    <xsl:for-each select="analysisSummary/configuration/property">
                        <tr>
                            <td class="name">
                                <xsl:value-of select="name"/>
                            </td>
                            <td class="std">
                                <xsl:value-of select="value"/>
                            </td>
                            <td class="std">
                                <xsl:value-of select="unit"/>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>

                <h3>Relative Statistics for
                    <xsl:value-of select="analysisSummary/modelVariable"/>
                    and
                    <xsl:value-of select="analysisSummary/referenceVariable"/>
                </h3>

                <table>
                    <tr class="table_header">
                        <td>
                            Statistical Term
                        </td>
                        <td>
                            Value
                        </td>
                    </tr>
                    <xsl:for-each select="analysisSummary/statistics/statistic[@type='relative']/properties/property">
                        <tr>
                            <td class="name">
                                <xsl:value-of select="name"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="value"/>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>

                <h3>Statistics for
                    <xsl:value-of select="analysisSummary/modelVariable"/>
                </h3>

                <table>
                    <tr class="table_header">
                        <td>
                            Statistical Term
                        </td>
                        <td>
                            Value
                        </td>
                    </tr>
                    <xsl:for-each select="analysisSummary/statistics/statistic[@type='model']/properties/property">
                        <tr>
                            <td class="name">
                                <xsl:value-of select="name"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="value"/>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>

                <h3>Statistics for
                    <xsl:value-of select="analysisSummary/referenceVariable"/>
                </h3>

                <table>
                    <tr class="table_header">
                        <td>
                            Statistical Term
                        </td>
                        <td>
                            Value
                        </td>
                    </tr>
                    <xsl:for-each select="analysisSummary/statistics/statistic[@type='reference']/properties/property">
                        <tr>
                            <td class="name">
                                <xsl:value-of select="name"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="value"/>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>

                <h3>Matchups</h3>

                <table class="matchup_table">
                    <xsl:for-each select="analysisSummary/matchups/matchup">
                        <tr>
                            <td class="matchup" rowspan="9">Matchup <xsl:value-of select="recordNumber"/>
                            </td>
                        </tr>
                        <xsl:for-each select="property">
                            <tr>
                                <td class="name">
                                    <xsl:value-of select="name"/>
                                </td>
                                <td class="value">
                                    <xsl:value-of select="value"/>
                                </td>
                            </tr>
                        </xsl:for-each>
                    </xsl:for-each>
                </table>

            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
