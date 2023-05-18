(function ($) {
    function init() {
        $('.PpoiField').each(function () {
            var $widget = $(this);
            var $overlay = $('.PpoiField__overlay', this);
            var $image = $('.PpoiField__overlay img', this);
            var $input = $widget.find('.PpoiField__input');

            console.log($overlay);

            function setPointer(x, y) {
                var $pointer = $overlay.find('.PpoiField__pointer');
                if (!$pointer.length) {
                    $pointer = $('<div class="PpoiField__pointer"></div>');
                    $overlay.append($pointer);
                }
                $pointer.css({'top': y, 'left': x});
            }

            function processInput() {
                var coords = $input.val().split(',');
                if (!isNaN(coords[0]) && !isNaN(coords[1]) && $image[0]) {
                    var x = Number(coords[0]) / 100 * $image[0].clientWidth;
                    var y = Number(coords[1]) / 100 * $image[0].clientHeight;
                    setPointer(x, y);
                }
            }

            $input.change(processInput);

            $image.click(function (e) {
                setPointer(e.offsetX, e.offsetY);
                var ex = Math.round($image[0].naturalWidth / $image[0].clientWidth * e.offsetX);
                var ey = Math.round($image[0].naturalHeight / $image[0].clientHeight * e.offsetY);
                var x = Math.round(ex / $image[0].naturalWidth * 100);
                var y = Math.round(ey / $image[0].naturalHeight * 100);
                $input.val(x + ',' + y);
            });

            processInput();
        });
    }

    $(document).ready(function () {
        init();
    });

    $(document).on('formset:added', function(event, $row, formsetName) {
        init();
    });
})(window.jQuery || django.jQuery);
