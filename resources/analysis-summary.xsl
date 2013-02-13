<?xml version="1.0" encoding="ISO-8859-1"?>
<!--
Copyright (C) 2013 Brockmann Consult GmbH (info@brockmann-consult.de)

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option)
any later version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along
with this program; if not, see http://www.gnu.org/licenses/gpl.html-->
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
                <script language="JavaScript" type="text/javascript">
                    function doMenu(item) {
                    obj = document.getElementById(item);
                    col = document.getElementById("id_" + item);
                    if (obj.style.display == "none") {
                    obj.style.display = "block";
                    col.innerHTML = "[hide]";
                    } else {
                    obj.style.display = "none";
                    col.innerHTML = "[show]";
                    }
                    }
                </script>
            </head>
            <body>

                <h2>Match-up Analysis Report</h2>

                <h3>Processing Information
                    <a href="JavaScript:doMenu('processing_info');" id="id_processing_info" class="hide">[hide]</a>
                </h3>

                <table style="display:block" id="processing_info">
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
                        <td class="name">Model variables:</td>
                        <td class="value">
                            <xsl:for-each select="analysisSummary/modelVariables/modelVariable">
                                <xsl:value-of select="text()"/>
                                <br/>
                            </xsl:for-each>
                        </td>
                    </tr>
                    <tr>
                        <td class="name">Reference variables:</td>
                        <td class="value">
                            <xsl:for-each select="analysisSummary/referenceVariables/referenceVariable">
                                <xsl:value-of select="text()"/>
                                <br/>
                            </xsl:for-each>
                        </td>
                    </tr>
                </table>

                <h3>Analysis Configuration
                    <a href="JavaScript:doMenu('config');" id="id_config" class="hide">[hide]</a>
                </h3>

                <table style="display:block" id="config">
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

                <xsl:for-each select="analysisSummary/statistics/statistic[@type='relative']">
                    <h3>Relative Statistics for
                        <xsl:value-of select="model_name"/>
                        with
                        <xsl:value-of select="ref_name"/>
                        <a class="hide">
                            <xsl:attribute name="href">JavaScript:doMenu('<xsl:value-of select="model_name"/>_<xsl:value-of select="ref_name"/>');
                            </xsl:attribute>
                            <xsl:attribute name="id">id_<xsl:value-of select="model_name"/>_
                                <xsl:value-of select="ref_name"/>
                            </xsl:attribute>
                            [hide]
                        </a>
                    </h3>

                    <table style="display:block">
                        <xsl:attribute name="id"><xsl:value-of select="model_name"/>_
                            <xsl:value-of select="ref_name"/>
                        </xsl:attribute>
                        <tr class="table_header">
                            <td>
                                Statistical Term
                            </td>
                            <td>
                                Value
                            </td>
                        </tr>
                        <xsl:for-each select="properties/property">
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
                </xsl:for-each>

                <xsl:for-each select="analysisSummary/statistics/statistic[@type='model']">
                    <h3>Statistics for
                        <xsl:value-of select="model_name"/>
                        <a class="hide">
                            <xsl:attribute name="href">JavaScript:doMenu('<xsl:value-of select="model_name"/>');
                            </xsl:attribute>
                            <xsl:attribute name="id">id_
                                <xsl:value-of select="model_name"/>
                            </xsl:attribute>
                            [hide]
                        </a>
                    </h3>

                    <table display="block">
                        <xsl:attribute name="id">
                            <xsl:value-of select="model_name"/>
                        </xsl:attribute>
                        <tr class="table_header">
                            <td>
                                Statistical Term
                            </td>
                            <td>
                                Value
                            </td>
                        </tr>
                        <xsl:for-each select="properties/property">
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
                </xsl:for-each>

                <xsl:for-each select="analysisSummary/statistics/statistic[@type='reference']">
                    <h3>Statistics for
                        <xsl:value-of select="ref_name"/>
                        <a class="hide">
                            <xsl:attribute name="href">JavaScript:doMenu('<xsl:value-of select="ref_name"/>');
                            </xsl:attribute>
                            <xsl:attribute name="id">id_
                                <xsl:value-of select="ref_name"/>
                            </xsl:attribute>
                            [hide]
                        </a>
                    </h3>

                    <table display="block">
                        <xsl:attribute name="id">
                            <xsl:value-of select="ref_name"/>
                        </xsl:attribute>
                        <tr class="table_header">
                            <td>
                                Statistical Term
                            </td>
                            <td>
                                Value
                            </td>
                        </tr>
                        <xsl:for-each select="properties/property">
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
                </xsl:for-each>

                <h3>Matchups
                    <a class="hide" href="JavaScript:doMenu('matchups');" id="id_matchups">[hide]</a>
                </h3>

                <table class="matchup" id="matchups" display="block">
                    <tr class="table_header">
                        <td>Record #</td>
                        <td>Time</td>
                        <td>Depth</td>
                        <td>Lat</td>
                        <td>Lon</td>
                        <td>Reference Time</td>
                        <td>Reference Depth</td>
                        <td>Reference Lat</td>
                        <td>Reference Lon</td>
                        <xsl:for-each select="analysisSummary/matchups/variables/var">
                            <td>
                                <xsl:value-of select="text()"/>
                            </td>
                        </xsl:for-each>
                    </tr>

                    <xsl:for-each select="analysisSummary/matchups/matchup">
                        <tr>
                            <td>
                                <xsl:value-of select="recordNumber"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="time"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="depth"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="lat"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="lon"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="reference_time"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="reference_depth"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="reference_lat"/>
                            </td>
                            <td class="value">
                                <xsl:value-of select="reference_lon"/>
                            </td>

                            <xsl:for-each select="property">
                                <td>
                                    <xsl:value-of select="value"/>
                                </td>
                            </xsl:for-each>

                        </tr>
                    </xsl:for-each>

                </table>

                <xsl:if test="/analysisSummary/taylorDiagrams">
                    <h3>Taylor Diagrams
                        <a class="hide" href="JavaScript:doMenu('taylor');" id="id_taylor">[hide]</a>
                    </h3>

                    <div display="block" id="taylor">
                        <xsl:for-each select="/analysisSummary/taylorDiagrams">
                            <img class="smaller">
                                <xsl:attribute name="src">
                                    <xsl:value-of select="taylorDiagram"/>
                                </xsl:attribute>
                            </img>
                        </xsl:for-each>
                    </div>
                </xsl:if>

                <xsl:if test="/analysisSummary/targetDiagram">
                    <h3>Target Diagram
                        <a class="hide" href="JavaScript:doMenu('target');" id="id_target">[hide]</a>
                    </h3>

                    <div display="block" id="target">
                        <img class="smaller">
                            <xsl:attribute name="src">
                                <xsl:value-of select="/analysisSummary/targetDiagram"/>
                            </xsl:attribute>
                        </img>
                    </div>
                </xsl:if>

                <xsl:if test="/analysisSummary/scatterPlots">
                    <h3>Scatter Plot(s)
                        <a class="hide" href="JavaScript:doMenu('scatter');" id="id_scatter">[hide]</a>
                    </h3>

                    <div display="block" id="scatter">
                        <xsl:for-each select="analysisSummary/scatterPlots">
                            <img class="smaller">
                                <xsl:attribute name="src">
                                    <xsl:value-of select="scatterPlot"/>
                                </xsl:attribute>
                            </img>
                            <br/>
                        </xsl:for-each>
                    </div>
                </xsl:if>

            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
