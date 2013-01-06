Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamPreviewController', {
    extend: 'Ext.app.Controller',

    views: [
        'preview.QualifiesForExamPreview'
    ],

    stores: [
        'RelatedStudents'
    ],

    models: [
        'Preview'
    ],

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],


    refs: [{
        ref: 'preview',
        selector: 'preview'
    }],

    init: function() {
        this.control({
            'viewport preview': {
                render: this._onRender
            }
        });
        this.mon(this.getPreviewModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        console.log('Render preview');
        this.periodid = this.getPreview().periodid;
        this.pluginsessionid = this.getPreview().pluginsessionid;
        this._loadPreviewModel();
    },

    _loadPreviewModel: function() {
        this.getPreviewModel().setParamsAndLoad(this.periodid, this.pluginsessionid, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onPreviewModelLoadSuccess(records);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },

    _onPreviewModelLoadSuccess: function(record) {
        this.previewRecord = record;
        var perioddata = this.previewRecord.get('perioddata');

        var relatedstudentsStore = this.getRelatedStudentsStore();
        relatedstudentsStore.loadData(perioddata.relatedstudents);
//        relatedstudentsStore.each(function (record) {
//            console.log(record.data);
//        });
    },

    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    }
});

