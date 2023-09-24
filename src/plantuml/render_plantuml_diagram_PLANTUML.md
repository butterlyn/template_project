```plantuml
@startuml
!theme materia
!pragma useVerticalIf on
skinparam note {
	BackgroundColor gray
	BorderColor lightgray
	FontColor white
}

TITLE Function: render_plantuml_diagram

START
PARTITION call function {
	:render_plantuml_diagram(file_path, diagram_format, theme, output_file_path);
	IF (default theme is supported?) THEN (yes)
		:use default theme;
	ELSE (no)
		#red: raise critical error;
	 	END
 	ENDIF
}
PARTITION resolve unset inputs {
	PARTITION resolve theme {
		IF (theme is not specified?) THEN (no)
			:set theme to default theme;
		(yes) ELSEIF (theme is supported?) THEN (no)
			#orange: log warning message;
			:use default theme;
		ELSE (yes)
			:use selected theme;
	 	ENDIF
	}
	PARTITION resolve output filepath {
		IF (output file path is specified?) THEN (no)
			:set output file path to
			current working directory;
		(yes) ELSEIF (output file path is a directory?) THEN (yes)
			:set file name to "output_diagram";
		ELSE (no)
	 	ENDIF
	}
}
PARTITION validate inputs {
	IF (input file exists?) THEN (no)
		#darkred: raise FileNotFoundError;
		END
	(yes) ELSEIF (output file path exists?) THEN (no)
		#darkred: raise FileNotFoundError;
		END
	(yes) ELSEIF (input file extension is supported?) THEN (no)
		#darkred: raise ValueError;
		END
	(yes) ELSEIF (diagram format is supported?) THEN (no)
		#darkred: raise ValueError;
		END
	ENDIF
}
PARTITION business logic {
	PARTITION get_required_plantuml_header_footer {
		:get required header and footer declarations; <<input>>
		#green:log debug message;
		NOTE LEFT
			required header and
			footer declarations
		END NOTE
		IF (plantuml markdown hint
is present in the file) THEN (yes)
			NOTE LEFT
				markdown hint:
			END NOTE
			:remove line containing
			plantuml markdown hint;
			NOTE LEFT
				this markdown hint will
				cause a rendering error
			END NOTE
			#green:log debug message;
			NOTE LEFT
				line containing plantuml
				markdown hint
			END NOTE
		ELSE (no)
		ENDIF
		IF (theme is already specified in file?) THEN (yes)
			:replace theme with specified theme; <<procedure>>
			#green:log debug message;
			NOTE LEFT
				location of already-existing
				theme in the file
			END NOTE
		ELSE (no)
		ENDIF
		:specify header and footer
		for plantUML diagram;
		:return header and footer; <<output>>
	}
	PARTITION render_plantuml_diagram {
		:create temporary copy of file; <<save>>
		#green:log debug message;
		NOTE LEFT:filepath of temporary file
		:get the required header and footer; <<input>>
		:append header and footer
		to temporary file; <<procedure>>
		:render plantUML diagram and
		save to output file path; <<procedure>>
		#green:log debug message;
		NOTE LEFT: output file path
		:delete temporary file;
		:return path of rendered diagram; <<output>>
	}
	:return path of rendered diagram file; <<output>>
}
STOP
@enduml