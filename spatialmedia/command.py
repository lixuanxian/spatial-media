#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Spatial Media Metadata Injector GUI 

GUI application for examining/injecting spatial media metadata in MP4/MOV files.
"""

import ntpath
import os
import sys
import traceback

try:
    from Tkinter import *
except ImportError:
    print("Tkinter library is not available.")
    exit(0)

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)
from spatialmedia import metadata_utils 


class Console(object):
    def __init__(self):
        self.log = []

    def append(self, text):
        print(text.encode('utf-8'))
        self.log.append(text)


class Application(Frame):
    def action_open(self):
     
        self.in_file = tmp_in_file

        self.set_message("Current 360 video: %s" % ntpath.basename(self.in_file))

        console = Console()
        parsed_metadata = metadata_utils.parse_metadata(self.in_file,
                                                        console.append)

        metadata = None
        audio_metadata = None
        if parsed_metadata:
            metadata = parsed_metadata.video
            audio_metadata = parsed_metadata.audio

        for line in console.log:
            if "Error" in line:
                self.set_error("Failed to load file %s"
                               % ntpath.basename(self.in_file))
                self.var_spherical.set(0)
                self.var_spatial_audio.set(0)
                self.disable_state()
                return

        self.enable_state()
        self.checkbox_spherical.configure(state="normal")

        infile = os.path.abspath(self.in_file)
        file_extension = os.path.splitext(infile)[1].lower()

        self.var_spherical.set(1)
        self.enable_spatial_audio = parsed_metadata.num_audio_channels == 4

        if not metadata:
            self.var_3d.set(0)

        if not audio_metadata:
            self.var_spatial_audio.set(0)

        if metadata:
            metadata = metadata.itervalues().next()

            if metadata.get("Spherical", "") == "true":
                self.var_spherical.set(1)
            else:
                self.var_spherical.set(0)

            if metadata.get("StereoMode", "") == "top-bottom":
                self.var_3d.set(1)
            else:
                self.var_3d.set(0)

        if audio_metadata:
            self.var_spatial_audio.set(1)
            print audio_metadata.get_metadata_string()

        

    def action_inject_delay(self):
        stereo = None
        if (self.var_3d.get()):
            stereo = "top-bottom"

        metadata = metadata_utils.Metadata()
        metadata.video = metadata_utils.generate_spherical_xml(stereo=stereo)

        if self.var_spatial_audio.get():
            metadata.audio = metadata_utils.SPATIAL_AUDIO_DEFAULT_METADATA 

        console = Console()
        metadata_utils.inject_metadata(
            self.in_file, self.save_file, metadata, console.append)
        self.set_message("Successfully saved file to %s\n"
                         % ntpath.basename(self.save_file))
        self.button_open.configure(state="normal")
        

    def action_inject(self):
        """Inject metadata into a new save file."""
        split_filename = os.path.splitext(ntpath.basename(self.in_file))
        base_filename = split_filename[0]
        extension = split_filename[1]
        self.save_options["initialfile"] = (base_filename
                                            + "_injected" + extension)
        self.save_file = tkFileDialog.asksaveasfilename(**self.save_options)
        if not self.save_file:
            return

        self.set_message("Saving file to %s" % ntpath.basename(self.save_file))

        self.master.after(100, self.action_inject_delay)

    
    def set_error(self, text):
        console = Console()
        console.append(text)

    def set_message(self, text):
        console = Console()
        console.append(text)

    def __init__(self, master=None):
        self.title = "Spatial Media Metadata Injector"
        self.open_options = {}
        self.open_options["filetypes"] = [("Videos", ("*.mov", "*.mp4"))]

        self.save_options = {}


        self.in_file = None
        self.enable_spatial_audio = True

def main():
    # app = Application(master=root)
    # app.mainloop()

if __name__ == "__main__":
    main()
