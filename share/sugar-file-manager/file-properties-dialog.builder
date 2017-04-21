<?xml version="1.0"?>
<interface>
  <requires lib="gtk+" version="2.16"/>
  <!-- interface-naming-policy project-wide -->
  <object class="GtkListStore" id="PermissionsModel">
    <columns>
      <!-- column-name user -->
      <column type="gchararray"/>
      <!-- column-name read -->
      <column type="gboolean"/>
      <!-- column-name write -->
      <column type="gboolean"/>
      <!-- column-name exec -->
      <column type="gboolean"/>
    </columns>
  </object>
  <object class="GtkDialog" id="FilePropertiesDialog">
    <property name="border_width">5</property>
    <property name="type_hint">normal</property>
    <child internal-child="vbox">
      <object class="GtkVBox" id="dialog-vbox1">
        <property name="visible">True</property>
        <property name="spacing">2</property>
        <child>
          <object class="GtkTable" id="table1">
            <property name="visible">True</property>
            <property name="n_rows">7</property>
            <property name="n_columns">2</property>
            <child>
              <object class="GtkLabel" id="name_label">
                <property name="visible">True</property>
                <property name="label" translatable="yes"> </property>
              </object>
              <packing>
                <property name="x_options"></property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="type_label">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="top_attach">1</property>
                <property name="bottom_attach">2</property>
                <property name="x_options"></property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="type_info">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="left_attach">1</property>
                <property name="right_attach">2</property>
                <property name="top_attach">1</property>
                <property name="bottom_attach">2</property>
                <property name="y_options">GTK_FILL</property>
              </packing>
            </child>
            <child>
              <object class="GtkEntry" id="name_entry">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="invisible_char">&#x2022;</property>
                <property name="primary_icon_sensitive">True</property>
                <property name="secondary_icon_sensitive">True</property>
              </object>
              <packing>
                <property name="left_attach">1</property>
                <property name="right_attach">2</property>
                <property name="y_options">GTK_FILL</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="size_label">
                <property name="visible">True</property>
                <property name="label" translatable="yes"> </property>
              </object>
              <packing>
                <property name="top_attach">2</property>
                <property name="bottom_attach">3</property>
                <property name="x_options"></property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkNotebook" id="size_notebook">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="show_tabs">False</property>
                <property name="show_border">False</property>
                <child>
                  <object class="GtkLabel" id="size_info">
                    <property name="visible">True</property>
                  </object>
                </child>
                <child type="tab">
                  <placeholder/>
                </child>
                <child>
                  <object class="GtkButton" id="find_size">
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="receives_default">True</property>
                  </object>
                  <packing>
                    <property name="position">1</property>
                  </packing>
                </child>
                <child type="tab">
                  <placeholder/>
                </child>
              </object>
              <packing>
                <property name="left_attach">1</property>
                <property name="right_attach">2</property>
                <property name="top_attach">2</property>
                <property name="bottom_attach">3</property>
                <property name="y_options">GTK_FILL</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="location_label">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="top_attach">4</property>
                <property name="bottom_attach">5</property>
                <property name="x_options"></property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="location_info">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="left_attach">1</property>
                <property name="right_attach">2</property>
                <property name="top_attach">4</property>
                <property name="bottom_attach">5</property>
                <property name="x_options">GTK_FILL</property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkHSeparator" id="hseparator1">
                <property name="sensitive">False</property>
              </object>
              <packing>
                <property name="right_attach">2</property>
                <property name="top_attach">3</property>
                <property name="bottom_attach">4</property>
                <property name="x_options"></property>
                <property name="y_options"></property>
                <property name="y_padding">8</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="accessed_label">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="top_attach">5</property>
                <property name="bottom_attach">6</property>
                <property name="x_options"></property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="accessed_info">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="left_attach">1</property>
                <property name="right_attach">2</property>
                <property name="top_attach">5</property>
                <property name="bottom_attach">6</property>
                <property name="x_options">GTK_FILL</property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="modified_label">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="top_attach">6</property>
                <property name="bottom_attach">7</property>
                <property name="x_options"></property>
                <property name="y_options"></property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="modified_info">
                <property name="visible">True</property>
              </object>
              <packing>
                <property name="left_attach">1</property>
                <property name="right_attach">2</property>
                <property name="top_attach">6</property>
                <property name="bottom_attach">7</property>
                <property name="x_options">GTK_FILL</property>
                <property name="y_options"></property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="position">2</property>
          </packing>
        </child>
        <child>
          <object class="GtkFrame" id="permissions-frame">
            <property name="visible">True</property>
            <property name="label_xalign">0</property>
            <property name="shadow_type">in</property>
            <child>
              <object class="GtkAlignment" id="alignment1">
                <property name="visible">True</property>
                <property name="left_padding">12</property>
                <child>
                  <object class="GtkTreeView" id="Permissions">
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="model">PermissionsModel</property>
                    <child>
                      <object class="GtkTreeViewColumn" id="User">
                        <property name="sizing">autosize</property>
                        <child>
                          <object class="GtkCellRendererText" id="user-renderer"/>
                          <attributes>
                            <attribute name="text">0</attribute>
                          </attributes>
                        </child>
                      </object>
                    </child>
                    <child>
                      <object class="GtkTreeViewColumn" id="Read">
                        <property name="sizing">autosize</property>
                        <child>
                          <object class="GtkCellRendererToggle" id="read-renderer"/>
                          <attributes>
                            <attribute name="active">1</attribute>
                          </attributes>
                        </child>
                      </object>
                    </child>
                    <child>
                      <object class="GtkTreeViewColumn" id="Write">
                        <property name="sizing">autosize</property>
                        <child>
                          <object class="GtkCellRendererToggle" id="write-renderer"/>
                          <attributes>
                            <attribute name="active">2</attribute>
                          </attributes>
                        </child>
                      </object>
                    </child>
                    <child>
                      <object class="GtkTreeViewColumn" id="Exec">
                        <property name="sizing">autosize</property>
                        <child>
                          <object class="GtkCellRendererToggle" id="exec-renderer"/>
                          <attributes>
                            <attribute name="active">3</attribute>
                          </attributes>
                        </child>
                      </object>
                    </child>
                  </object>
                </child>
              </object>
            </child>
            <child type="label">
              <object class="GtkLabel" id="permissions_label">
                <property name="visible">True</property>
                <property name="use_markup">True</property>
              </object>
            </child>
          </object>
          <packing>
            <property name="position">3</property>
          </packing>
        </child>
        <child internal-child="action_area">
          <object class="GtkHButtonBox" id="dialog-action_area1">
            <property name="visible">True</property>
            <property name="layout_style">end</property>
            <child>
              <object class="GtkButton" id="acept_button">
                <property name="label">gtk-ok</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="use_stock">True</property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">False</property>
                <property name="position">0</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">False</property>
            <property name="pack_type">end</property>
            <property name="position">0</property>
          </packing>
        </child>
      </object>
    </child>
    <action-widgets>
      <action-widget response="1">acept_button</action-widget>
    </action-widgets>
  </object>
</interface>
