<%
	buildtime = middleware.call_sync('system.build_time')
	motd = middleware.call_sync('system.advanced.config')['motd']
%>\

	X-NAS (c) 2026-${buildtime.year}, Xloud
	All rights reserved.
	X-NAS is built on open-source components released under their
	own respective licenses.

	For more information, documentation, help or support, go here:
	https://xloud.tech

Warning: the supported mechanisms for making configuration changes
are the X-NAS WebUI, CLI, and API exclusively. ALL OTHERS ARE
NOT SUPPORTED AND WILL RESULT IN UNDEFINED BEHAVIOR AND MAY
RESULT IN SYSTEM FAILURE.

% if motd:
${motd}
% endif
