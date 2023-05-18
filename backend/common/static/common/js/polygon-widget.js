(function ($) {
    function init() {
        var $block = $('.block.js-sc');
        $block.each( async function() {
            const act = '_active';

            if (!$block.length) return;

            const maxWidth = 1920;
            const maxHeight = 1080;
            let widthImage = $(this).find($('.js-sc-wrapper')).innerWidth()
            let heightImage = $(this).find($('.js-sc-wrapper')).innerHeight()
            if (widthImage < heightImage) {
                if (widthImage > maxWidth) {
                    heightImage = Math.round((heightImage *= maxWidth / widthImage));
                    widthImage = maxWidth;
                }
            } else if (heightImage > maxHeight) {
                widthImage = Math.round((widthImage *= maxHeight / heightImage));
                heightImage = maxHeight;
            }
            console.log(heightImage);
            console.log(widthImage);


            // Elements

            const $input = $(this).find($('.js-sc-i'));

            const $wrapper = $(this).find($('.js-sc-wrapper'));
            const  $svg = $(this).find($('.js-sc-svg'));
            const $polygon = $(this).find($('.js-sc-polygon'));

            // Controls

            const $tagOutput = $(this).find($('.js-sc-tag'));
            const $pointsOutput = $(this).find($('.js-sc-points'));

            const $undo = $(this).find($('.js-sc-undo'));
            const $refresh = $(this).find($('.js-sc-refresh'));

            // State

            let points = [];
            let tag = true;

            // Sizes

            let ol,ot,diff,iw,bw


            if ($wrapper.length) {
                bw = $wrapper.innerWidth();
                ot = $wrapper.offset().top;
                ol = $wrapper.offset().left;
                iw = $svg[0].getAttribute('viewBox').split(' ')[2];
                if(iw.indexOf('None') == -1) {
                    diff = iw / bw;
                } else {
                    const img = $(this).find($('.sc__image'))
                    $.get(img.attr('src'), (data) => {
                        console.log(data.querySelector('svg').getAttribute('viewBox'));
                        $svg[0].setAttribute('viewBox', data.querySelector('svg').getAttribute('viewBox'))
                        console.log(data.querySelector('svg').getAttribute('viewBox').split(' ')[2]);
                        iw = data.querySelector('svg').getAttribute('viewBox').split(' ')[2]
                        diff = iw / bw;
                    })
                }

            };

            // Events

            $svg.on('click', clickSignal);

            $refresh.on('click', refreshSignal);
            $undo.on('click', undoSignal);

            $tagOutput.on('click', tagOutputSignal);
            $pointsOutput.on('click', pointsOutputSignal);

            // Signals && Methods

            function clickSignal(e) {
                console.log(e);
                const left = e.pageX;
                const top = e.pageY;

                const t_point = top - ot;
                const l_point = left - ol;

                const svg_t_point = Math.round((t_point * diff) * 1000) / 1000;
                const svg_l_point = Math.round((l_point * diff) * 1000) / 1000;

                points.push('' + svg_l_point + ',' + svg_t_point + '');

                makerString();
            }

            function refreshSignal() {
                points = [].concat.apply([]);
                makerString();
            }

            function undoSignal() {
                points.pop();
                makerString();
            }

            function tagOutputSignal() {
                tag = true;

                $pointsOutput.removeClass(act);
                $tagOutput.addClass(act);

                makerString();
            }

            function pointsOutputSignal() {
                tag = false;

                $tagOutput.removeClass(act);
                $pointsOutput.addClass(act);

                makerString();
            }

            function makerString() {
                let str = '';

                for (var i = 0; i < points.length; i++) {
                    var point = points[i];

                    str += point + ' ';
                }

                updateInput(str);
                updatePolygon(str);
            }

            function updateInput(str) {
                $input.val((str.replace(' ', '') !== '') ? '<polygon points="' + str + '"></polygon>' : '')
            }

            function updatePolygon(str) {
                $polygon.attr('points', str);
            }
        })


    }

    $(document).ready(function () {
        setTimeout(init, 1000);
        init();
    });
})(window.jQuery || django.jQuery);
