<!DOCTYPE html>
<html>
	<head>
		<title>
			{% block title %}Interactive Video Geotagging{% endblock %}
		</title>
		{% load compress %}
		{% compress css file %} 
			<link rel="stylesheet" type="text/x-sass" href="/static/css/style.sass"></link>
		{% endcompress %}
		
		<link rel="stylesheet" href="static/css/blueprint/screen.css" type="text/css" media="screen, projection">
		<link rel="stylesheet" href="static/css/blueprint/print.css" type="text/css" media="print">
		<link rel="stylesheet" href="static/css/flick/jquery-ui-1.8.20.custom.css" type="text/css"></link>
		<link rel="stylesheet" href="http://vjs.zencdn.net/c/video-js.css" type="text/css"></link>
		
		{% block osmscripts %}
		{% endblock %}
		<script type="text/javascript" src="http://vjs.zencdn.net/c/video.js"></script>
		<script type="text/javascript" src="/static/js/jquery-1.7.2.min.js"></script>
		<script type="text/javascript" src="/static/js/jquery-ui-1.8.20.custom.min.js"></script>
		<script type="text/javascript" src="/static/js/init.js"></script>
				
		{% block scripts %}
		{% endblock %}
		
	</head>

	<body id="body" class="" onload="bodyinit();">
		
		
			<div class="span-2 first">
				<a href="/" >
					<img id="logo" src="static/images/logo.png" ></img>
				</a>
			</div>
			<div class="span-22 last">
				<h1 class="ui-state-highlight ui-priority-primary">Application for Playback and Composition of Geotagged Videos</h1>			
			</div>
			{% block content %}
			{% endblock %}
		
		
	</body>
</html>
		