/* Copyright (c) 2019, Orange
 *
 * Author: Philippe Merle <philippe.merle@inria.fr>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
 * (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
 * OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
package org.alloytools.nativecode.util;

import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Enumeration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;

public class NativeCode {

    static class Platform {

        public Platform(String osnames, String osarch, String dir) {
            try {
                this.osarch = Pattern.compile(osarch, Pattern.CASE_INSENSITIVE);
                this.osname = Pattern.compile(osnames, Pattern.CASE_INSENSITIVE);
                this.dir = dir;
            } catch (Exception e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        }

        final Pattern osname;
        final Pattern osarch;
        final String  dir;
    }

    static Map<String,Path> cached      = new ConcurrentHashMap<>();

    public static Platform  AMD64_LINUX = new Platform("linux", "amd64", "amd64-linux");
    // public static Platform x86_64_LINUX = new Platform("linux", "x86-64",
    // "linux_x86_64");
    // public static Platform X86_FREEBSD = new Platform("freebsd", "x86.*",
    // "x86-freebsd");
    public static Platform   X86_LINUX   = new Platform("linux", ".*86.*", "x86-linux");
    public static Platform   X86_MAC     = new Platform("mac\\s*os.*", "ppc|power|powerpc.*|x86.*", "x86-mac");
    public static Platform   X86_WINDOWS = new Platform("win.*", "x86.*", "x86-windows");
    public static Platform[] platforms   = {
                                            AMD64_LINUX,
                                            // x86_64_LINUX, X86_FREEBSD,
                                            X86_LINUX, X86_MAC, X86_WINDOWS
    };

    public static Platform   platform    = findPlatform();

    @SuppressWarnings("unused" )
    public static boolean loadlibrary(Path cache, String name) throws RuntimeException {
        try {
            if (platform.dir == null)
                return false;

            Platform p = platform;
            String libraryName = System.mapLibraryName(name);

            String file = platform.dir + "/" + libraryName;
            Enumeration<URL> enumeration = NativeCode.class.getClassLoader().getResources(file);
            if (!enumeration.hasMoreElements()) {
                // PM: Replaced System.out by System.err.
                System.err.println("Could not find native lib " + file);
                return false;
            }

            URL resource = enumeration.nextElement();
// PM: Commented out debug traces.
//            System.out.println("Found native lib '" + resource + "'");

            Path to = cached.computeIfAbsent(name, (k) -> {
                try {
                    if (cache == null) {
                        Path tox = Files.createTempFile(name, libraryName);
                        tox.toFile().deleteOnExit();
                        return tox;
                    } else {
                        cache.toFile().mkdirs();
                        return cache.resolve(libraryName);
                    }
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });

            Files.copy(resource.openStream(), to, StandardCopyOption.REPLACE_EXISTING);
            System.load(to.toFile().getAbsolutePath());
            return true;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private static Platform findPlatform() {
        String os = System.getProperty("os.name");
        String arch = System.getProperty("os.arch");
// PM: Commented out debug traces.
//        System.out.println("OS _ ARCH = '" + os + "' - '" + arch + "'");
        for (Platform p : platforms) {
            if (p.osarch.matcher(arch).matches() && p.osname.matcher(os).matches()) {
// PM: Commented out debug traces.
//                System.out.println("Found = '" + p.dir);
                return platform = p;
            }
        }
        return new Platform(".*", ".*", null);
    }
}
