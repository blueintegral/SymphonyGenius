Symphony Genius
===============

Instructions
------------
*	Install Heroku Toolbelt
*	`heroku login`
*	`heroku git:clone --app symph`
*	`python server.py`
*	`sudo foreman start`
*	Set config vars in .env file


Libraries:
----------
*	PyMongo: http://api.mongodb.org/python/current
*	Cloudinary: https://devcenter.heroku.com/articles/cloudinary
*	midi2ly: http://lilypond.org/doc/v2.14/Documentation/usage/invoking-midi2ly
*	LilyPond: http://lilypond.org/doc/v2.14/Documentation/usage/command_002dline-usage
*	Bootstrap: http://twitter.github.com/bootstrap
*	HTML5 Boilerplate: http://html5boilerplate.com
*	jQuery Fancybox 2 (Removed): http://fancyapps.com/fancybox/


TODO:
-----
Add Git Deploy (Todo): https://github.com/mislav/git-deploy
Upload top 10 classical songs / scrape downloaded dump.
Test bars / offset variables.


SNIPPETS:
---------
Add music box.





FancyBox Stuff.
<link rel="stylesheet" href="{{url_for('static', filename='css/jquery.fancybox.css')}}" type="text/css" media="screen" />
<script type="text/javascript" src="{{url_for('static', filename='js/jquery.fancybox.pack.js')}}"></script>
$(".fancybox").fancybox({
    beforeLoad: function() {
        this.title = $(this.element).attr('caption');
    }
});
