Ext.define('devilry.examiner.AssignmentView', {
    extend: 'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
    alias: 'widget.examiner-assignmentview',

    requires: [
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
        'devilry.extjshelpers.charts.PointsOfGroupsOnSingleAssignment'
    ],

    config: {
        assignment_recordcontainer: undefined,
        assignmentmodelname: undefined,
        assignmentid: undefined,
        assignmentgroupstore: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        Ext.apply(this, {
            title: 'Todo-list',
            store: this.assignmentgroupstore,
            toolbarExtra: ['->', {
               xtype: 'button',
               scale: 'large',
               text: 'Download all deliveries',
               listeners: {
                   scope: this,
                   click: this.onDownload
               }
            }, {
               xtype: 'button',
               scale: 'large',
               text: 'Manage assignment groups (students)',
               listeners: {
                   scope: this,
                   click: this.onStudents
               }
            }],
            
            helpTpl: Ext.create('Ext.XTemplate',
                '<div class="section helpsection">',
                '   {todohelptext}',
                '   <p>Choose <span class="menuref">Manage assignment groups (students)</span> to view all groups, and to give feedback to multiple groups.</p>',
                '   <p>You may want to <span class="menuref">Download all deliveries</span> as a zip file instead of downloading the delivery for each group separately. This will download all deliveries from all assignment groups where you are examiner on this assignment, not just the deliveries in your todo-list.</p>',
                '</div>'
            ),

            onSelectGroup: function(grid, assignmentgroupRecord) {
                var url = Ext.String.format('../assignmentgroup/{0}',
                    assignmentgroupRecord.data.id
                );
                window.location.href = url;
            },
        });
        this.callParent(arguments);

        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this.onLoadAssignmentSuccess,
            failure: this.onLoadAssignmentFailure
        });
        this.loadTodoListForAssignment(this.assignmentid);
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignment_recordcontainer.setRecord(record);
        //this.onStudents();
    },

    onLoadAssignmentFailure: function() {
        throw "Failed to load assignment";
    },

    onStudents: function(button) {
        this.hide();
        var studentswindow = Ext.create('Ext.window.Window', {
            title: 'Students',
            width: 926,
            height: 500,
            layout: 'fit',
            maximizable: false,
            modal: true,
            maximized: true,
            items: {
                xtype: 'studentsmanager',
                assignmentgroupstore: this.assignmentgroupstore,
                assignmentid: this.assignmentid,
                assignmentrecord: this.assignment_recordcontainer.record,
                deadlinemodel: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDeadline'),
                gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.examiner.SimplifiedConfig'),
                isAdministrator: false
            },
            listeners: {
                scope: this,
                close: function() {
                    this.show();
                    this.loadTodoList();
                }
            }
        });
        studentswindow.show();
    },

    onDownload: function() {
        window.location.href = Ext.String.format('compressedfiledownload/{0}', this.assignmentid);
    }
});
