function dynload_init()
{
    $(".nav-item a").on("click", function(e)
    {
        if ($("#logged-in").length == 0)
            return;

        e.preventDefault();

        var path = this.href.split(document.location.host)[1];
        var item = $(this);
        history.pushState(history.state, path, path);
        $("#content").load(path+"?ajax=1", function(response) {
            if (response == "ERROR") {
                document.location = path;
                return;
            }

            $(".nav-item").removeClass('active');
            item.parent().addClass('active');
        });
    });
}

$(document).ready(dynload_init);
