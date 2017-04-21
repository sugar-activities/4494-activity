<?xml version="1.0"?>
<interface>
  <requires lib="gtk+" version="2.16"/>
  <!-- interface-naming-policy toplevel-contextual -->
  <object class="GtkListStore" id="BookmarksStore">
    <columns>
      <!-- column-name gchararray1 -->
      <column type="gchararray"/>
      <!-- column-name gchararray2 -->
      <column type="gchararray"/>
      <!-- column-name gchararray3 -->
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkListStore" id="MountsStore">
    <columns>
      <!-- column-name gchararray1 -->
      <column type="gchararray"/>
      <!-- column-name gchararray2 -->
      <column type="gchararray"/>
      <!-- column-name gchararray3 -->
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkListStore" id="FileModel">
    <columns>
      <!-- column-name icon_pixbuf -->
      <column type="GdkPixbuf"/>
      <!-- column-name icon_name -->
      <column type="gchararray"/>
      <!-- column-name display_name -->
      <column type="gchararray"/>
      <!-- column-name file_name -->
      <column type="gchararray"/>
      <!-- column-name file_uri -->
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkHBox" id="Area">
    <property name="visible">True</property>
    <child>
      <object class="GtkVBox" id="PATHS">
        <property name="visible">True</property>
        <child>
          <object class="GtkScrolledWindow" id="scrolledwindow1">
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="hscrollbar_policy">never</property>
            <property name="vscrollbar_policy">automatic</property>
            <child>
              <object class="GtkTreeView" id="Bookmarks">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="model">BookmarksStore</property>
                <property name="headers_clickable">False</property>
                <property name="search_column">0</property>
                <child>
                  <object class="GtkTreeViewColumn" id="BookmarksColumn">
                    <property name="sizing">autosize</property>
                    <child>
                      <object class="GtkCellRendererPixbuf" id="Bookmarks-pix-cell"/>
                      <attributes>
                        <attribute name="icon-name">0</attribute>
                      </attributes>
                    </child>
                    <child>
                      <object class="GtkCellRendererText" id="Bookmarks-text-cell"/>
                      <attributes>
                        <attribute name="text">1</attribute>
                      </attributes>
                    </child>
                  </object>
                </child>
              </object>
            </child>
          </object>
          <packing>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <object class="GtkScrolledWindow" id="MountsArea">
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="hscrollbar_policy">never</property>
            <property name="vscrollbar_policy">automatic</property>
            <child>
              <object class="GtkTreeView" id="Mounts">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="model">MountsStore</property>
                <property name="headers_clickable">False</property>
                <property name="search_column">0</property>
                <child>
                  <object class="GtkTreeViewColumn" id="MountsColumn">
                    <child>
                      <object class="GtkCellRendererPixbuf" id="mounts-pix-cell"/>
                      <attributes>
                        <attribute name="icon-name">0</attribute>
                      </attributes>
                    </child>
                    <child>
                      <object class="GtkCellRendererText" id="mounts-name-cell"/>
                      <attributes>
                        <attribute name="text">1</attribute>
                      </attributes>
                    </child>
                  </object>
                </child>
              </object>
            </child>
          </object>
          <packing>
            <property name="position">1</property>
          </packing>
        </child>
      </object>
      <packing>
        <property name="expand">False</property>
        <property name="position">0</property>
      </packing>
    </child>
    <child>
      <object class="GtkVSeparator" id="vseparator1">
        <property name="visible">True</property>
      </object>
      <packing>
        <property name="expand">False</property>
        <property name="position">1</property>
      </packing>
    </child>
    <child>
      <object class="GtkVBox" id="vbox1">
        <property name="visible">True</property>
        <child>
          <object class="GtkHBox" id="FilePathBox">
            <property name="visible">True</property>
            <child>
              <object class="GtkLabel" id="Path">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkEntry" id="FileNameEntry">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="invisible_char">&#x2022;</property>
                <property name="secondary_icon_stock">gtk-apply</property>
                <property name="primary_icon_activatable">True</property>
                <property name="secondary_icon_activatable">True</property>
                <property name="primary_icon_sensitive">True</property>
                <property name="secondary_icon_sensitive">True</property>
              </object>
              <packing>
                <property name="position">1</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <object class="GtkScrolledWindow" id="FileArea">
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="hscrollbar_policy">automatic</property>
            <property name="vscrollbar_policy">automatic</property>
            <child>
              <object class="GtkIconView" id="FileView">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="model">FileModel</property>
                <property name="row_spacing">1</property>
                <property name="column_spacing">1</property>
                <property name="margin">8</property>
                <property name="item_padding">1</property>
                <child>
                  <object class="GtkCellRendererPixbuf" id="icon"/>
                  <attributes>
                    <attribute name="icon-name">1</attribute>
                    <attribute name="pixbuf">0</attribute>
                  </attributes>
                </child>
                <child>
                  <object class="GtkCellRendererText" id="name">
                    <property name="xalign">0.50999999046325684</property>
                    <property name="alignment">center</property>
                  </object>
                  <attributes>
                    <attribute name="text">2</attribute>
                  </attributes>
                </child>
              </object>
            </child>
          </object>
          <packing>
            <property name="position">1</property>
          </packing>
        </child>
      </object>
      <packing>
        <property name="position">2</property>
      </packing>
    </child>
  </object>
</interface>
