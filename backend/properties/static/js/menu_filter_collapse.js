(function($){
ListFilterCollapsePrototype = {
    bindToggle: function(){
        var that = this;

        try{
            var stored = new Set(JSON.parse(localStorage.getItem('hiddenElements')))
        } catch (e){
            console.log(e)
        }

        this.$filterEl.click(function(){
            var stored = new Set(JSON.parse(localStorage.getItem('hiddenElements')))
            if(that.$filterList.is(":hidden")){
                stored.delete(that.$filterEl[0].innerText)
                that.$filterEl.addClass('changelist-custom-heading--expanded');
            }
            else{
                stored.add(that.$filterEl[0].innerText)
                that.$filterEl.removeClass('changelist-custom-heading--expanded');
            }
            localStorage.setItem('hiddenElements', JSON.stringify(Array.from(stored)))
            that.$filterList.slideToggle();
        });
    },
    init: function(filterEl) {
        this.$filterEl = $(filterEl).addClass('changelist-custom-heading');
        var stored = new Set(JSON.parse(localStorage.getItem('hiddenElements')));
        if(stored === undefined || stored === null || Object.keys(stored).length === 0){
            localStorage.setItem('hiddenElements', JSON.stringify(Array.from(stored)))
        }
        if(stored.has(filterEl.innerText)){
            this.$filterList = this.$filterEl.next('ul').hide();
        }
        else {
            this.$filterList = this.$filterEl.next('ul').show();
            this.$filterEl.addClass('changelist-custom-heading--expanded')
        }
        this.bindToggle();
    }
}
function ListFilterCollapse(filterEl) {
    this.init(filterEl);
}
ListFilterCollapse.prototype = ListFilterCollapsePrototype;

$(document).ready(function(){
    $('#changelist-filter').children('h3').each(function(){
        var collapser = new ListFilterCollapse(this);
    });
});
})(django.jQuery);