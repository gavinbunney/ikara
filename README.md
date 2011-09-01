## Ikara - forget svn blame, this is Bamboo blame!

*Rule with an iron first - punish failure... automatically!*

### Summary

Ikara is a <a href="http://www.atlassian.com/software/bamboo/">Bamboo</a> build watcher from <a href="http://4impact.com.au">4impact</a> that punishes those
who break the build. Named after an Australian Aboriginal word for "throwing stick", it is based on <a href="https://github.com/codedance/Retaliation">retailiation</a> for Jenkins,
but designed to work with Atlassian Bamboo.

Build breakages are detected through polling the failed-build rss feed. When a failed build is detected,
the Missle Launcher goes to work 'notifying' the offenders!

<img src="https://github.com/4impact/ikara/raw/master/images/thunder.jpg"/>

### How to Use

  1.  Mount your <a href="http://www.dreamcheeky.com/thunder-missile-launcher">Dream Cheeky Thunder USB Missile Launcher</a> 
      in a central and fixed location.

  2.  Install libusb, PyUSB and <a href="http://www.feedparser.org/">feedparser</a> for your operating system
  
  3.  Download the <a href="https://raw.github.com/4impact/ikara/master/ikara.py">ikara.py</a> 
      script onto the system connected to your missile launcher.

  4.  Modify the Bamboo configuration in the `ikara.py` script to define the Bamboo server details.
      
      ```python
BAMBOO_HOST      = '10.53.116.60'
BAMBOO_PORT      = '8085'
BAMBOO_USERNAME  = 'gbunney'
BAMBOO_PASSWORD  = 'gbunney'
```

  5.  Modify your `COMMAND_SETS` in the `ikara.py` script to define your targeting 
      commands for each one of your build-braking coders (their user ID as configured in Bamboo).
 
      You can test a set by calling ikara.py with the target name. e.g.:  

      ```python
python ikara.py "[developer's user name]"
```

  6.  Start listening for failed build events by running the command:

      ```python
python ikara.py monitor <build-key(s)>
```

      Where `<build-key(s)>` is a comma separate list of plan keys for the builds you want to monitor.

      e.g. to monitor both TRUNK and PLUGINS:
      ```python
python ikara.py monitor TRUNK,PLUGINS
```

  7.  Sit back, relax and let Ikara do your dirty 'build-cop' work for you
  
### Other Uses
 
`ikara.py` also doubles as a command-line scripting API for the *Dream Cheeky 
USB Missile Launcher*.  You can invoke it to control the device from a script or 
command-line as follows:

      ikara.py zero
      ikara.py right 3000
      ikara.py up 700
      ikara.py fire 1
        
