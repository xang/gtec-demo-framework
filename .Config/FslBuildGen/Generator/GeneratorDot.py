#!/usr/bin/env python3

#****************************************************************************************************************************************************
# Copyright (c) 2014 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
#    * Neither the name of the Freescale Semiconductor, Inc. nor the names of
#      its contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#****************************************************************************************************************************************************

from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union
import os
import os.path
import subprocess
from FslBuildGen import IOUtil
from FslBuildGen.Config import Config
from FslBuildGen.DataTypes import AccessType
from FslBuildGen.DataTypes import PackageType
from FslBuildGen.Generator.GeneratorBase import GeneratorBase
from FslBuildGen.Packages.Package import Package
from FslBuildGen.Packages.Package import PackageDependency
from FslBuildGen.Packages.Package import PackageExternalDependency
#from FslBuildGen.Exceptions import *

class GeneratorDot(GeneratorBase):
    def __init__(self, config: Config, packages: List[Package], platformName: str) -> None:
        super(GeneratorDot, self).__init__()

        self.UseVariantNames = True
        self.RequireExecutable = True
        self.ShowExternals = False

        packageList = packages
        if self.RequireExecutable:
            packageList = self.FilterBasedOnExecutableDemand(packages)
            if len(packageList) <= 0:
                packageList = packages


        #dotFile = self.CreateDirectDependencies(config, packageList, platformName)
        #dotFile = self.CreateAllDependencies(config, packageList, platformName)
        #dotFile = self.CreateSimpleDependencies(config, packageList, platformName)
        dotFile = self.CreateSimpleDependencies2(config, packageList, platformName)

        content = "\n".join(dotFile)

        tmpFile = "TmpDependencies_%s.dot" % (platformName)
        outputFile = "Dependencies_%s.png" % (platformName)

        IOUtil.WriteFile(tmpFile, content)

        # "dot -Tpng -o test.png Dependencies_Yocto.dot"
        try:
            subprocess.call(["dot", "-Tpng", "-o%s" % outputFile, tmpFile])
            os.remove(tmpFile)
        except Exception as ex:
            print("WARNING: Failed to execute dot, is it part of the path?")
            os.remove(tmpFile)
            raise


    def CreateDirectDependencies(self, config: Config, packages: List[Package], platformName: str) -> List[str]:
        dotFile = []
        dotFile.append('digraph xmlTest')
        dotFile.append('{')
        dotFile.append('  overlap=scale;')
        dotFile.append('  splines=true;')
        dotFile.append('  edge [len=1];')

        laterPrivate = []
        laterLink = []

        #groups = {}

        for package in packages:
            if not package.Name.startswith('SYS_'):
                if package.ResolvedDirectDependencies is None:
                    raise Exception("Invalid package")

                for dep1 in package.ResolvedDirectDependencies:
                    if dep1.Access == AccessType.Link:
                        laterLink.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                    elif dep1.Access == AccessType.Private:
                        laterPrivate.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                    else:
                        dotFile.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                if self.ShowExternals:
                    for dep2 in package.ResolvedDirectExternalDependencies:
                        dotFile.append('  "%s" -> "%s"' % (self.GetName(package), dep2.Name))

        if len(laterPrivate):
            dotFile.append('  edge [color="#2F4F4F", style=dashed]')
            for entry in laterPrivate:
                dotFile.append(entry)

        if len(laterLink):
            dotFile.append('  edge [color=Blue, style=dotted]')
            for entry in laterLink:
                dotFile.append(entry)

        dotFile.append('}')
        return dotFile


    def CreateAllDependencies(self, config: Config, packages: List[Package], platformName: str) -> List[str]:
        dotFile = []
        dotFile.append('digraph xmlTest')
        dotFile.append('{')
        dotFile.append('  overlap=scale;')
        dotFile.append('  splines=true;')
        dotFile.append('  edge [len=1];')

        laterPrivate = []
        laterLink = []

        for package in packages:
            if not package.Name.startswith('SYS_'):
                for dep1 in package.ResolvedAllDependencies:
                    if dep1.Access == AccessType.Link:
                        laterLink.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                    elif dep1.Access == AccessType.Private:
                        laterPrivate.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                    else:
                        dotFile.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                if self.ShowExternals:
                    for dep2 in package.ResolvedDirectExternalDependencies:
                        dotFile.append('  "%s" -> "%s"' % (self.GetName(package), dep2.Name))

        if len(laterPrivate):
            dotFile.append('  edge [color="#2F4F4F", style=dashed]')
            for entry in laterPrivate:
                dotFile.append(entry)

        if len(laterLink):
            dotFile.append('  edge [color=Blue, style=dotted]')
            for entry in laterLink:
                dotFile.append(entry)

        dotFile.append('}')
        return dotFile


    def CreateSimpleDependencies(self, config: Config, packages: List[Package], platformName: str) -> List[str]:
        dotFile = []
        dotFile.append('digraph xmlTest')
        dotFile.append('{')
        dotFile.append('  overlap=scale;')
        dotFile.append('  splines=true;')
        dotFile.append('  edge [len=1];')

        for package in packages:
            if not package.Name.startswith('SYS_'):
                for dep1 in package.ResolvedAllDependencies:
                    if not self.IsAvailableFromDependentPackage(dep1, package):
                        dotFile.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                if self.ShowExternals:
                    for dep2 in package.ResolvedDirectExternalDependencies:
                        if not self.IsExternalAvailableFromDependentPackage(dep2, package.ResolvedDirectDependencies):
                            dotFile.append('  "%s" -> "ext: %s"' % (self.GetName(package), dep2.Name))

        dotFile.append('}')
        return dotFile


    def IsAvailableFromDependentPackage(self, dep: PackageDependency, package: Package) -> bool:
        for entry in package.ResolvedAllDependencies:
            if entry.Name != dep.Name:
                if self.ExistIn(entry.Package.ResolvedAllDependencies, dep.Name):
                    return True
        return False


    def IsExternalAvailableFromDependentPackage(self, dep: PackageExternalDependency, otherDeps: List[PackageDependency]) -> bool:
        for entry in otherDeps:
            if self.ExistIn(entry.Package.ResolvedDirectExternalDependencies, dep.Name):
                return True
        return False


    # Was multiple defined, enabled the last one as that is the one the code has been calling
    #def ExistIn(self, dependencies, name):
    #    for dep in dependencies:
    #        if dep.Name == name:
    #            return True;
    #    return False;


    def GetRootNamespace(self, config: Config, namespace: Optional[str]) -> str:
        if namespace is None:
            return ''
        if not '.' in namespace:
            return namespace
        return namespace[0:namespace.find('.')]


    def GetRootName(self, config: Config, package: Package) -> str:
        if package.Namespace is None or package.AbsoluteBuildPath is None:
            raise Exception("Invalid package")
        if not '.' in package.Namespace:
            if 'ThirdParty' in package.AbsoluteBuildPath:
                return 'ThirdParty'
            return ""
        return ""


    def GroupPackages(self, config: Config, packages: List[Package]) -> Dict[str, List[Package]]:
        groupDict = {}  # type: Dict[str, List[Package]]
        for package in packages:
            rootNamespace = self.GetRootNamespace(config, package.Namespace)
            #rootNamespace = self.GetRootName(config, package)
            if rootNamespace not in groupDict:
                groupDict[rootNamespace] = []
            groupDict[rootNamespace].append(package)

        for entry in list(groupDict.values()):
            entry.sort(key=lambda s: s.Name.lower())
        return groupDict


    def CreateSimpleDependencies2(self, config: Config, packages: List[Package], platformName: str) -> List[str]:
        #groups = self.GroupPackages(config, packages)

        dotFile = []
        dotFile.append('digraph xmlTest')
        dotFile.append('{')
        dotFile.append('  overlap=scale;')
        dotFile.append('  splines=true;')
        dotFile.append('  edge [len=1];')

        laterPrivate = []
        laterLink = []

        #laterGroups = []
        #for key, group in groups.iteritems():
        #    if len(key) > 0 and len(group) > 1:
        #        laterGroups.append('  subgraph cluster_{0} {{'.format(key))
        #        #laterGroups.append('      style=filled;')
        #        #laterGroups.append('      color=lightgrey;')
        #        laterGroups.append('      node [style=filled];')
        #        for package in group:
        #            laterGroups.append('      "{0}";'.format(self.GetName(package)))
        #        laterGroups.append('      label = "{0}";'.format(key))
        #        laterGroups.append('  }')

        #if len(laterGroups):
        #    dotFile = dotFile + laterGroups

        for package in packages:
            if not package.Name.startswith('SYS_'):
                for dep1 in package.ResolvedDirectDependencies:
                    if dep1.Access == AccessType.Private:
                        laterPrivate.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                    elif dep1.Access == AccessType.Link:
                        laterLink.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                    else:
                        if not self.IsAvailableFromDependentPackage2(dep1, package):
                            dotFile.append('  "%s" -> "%s"' % (self.GetName(package), self.GetName(dep1.Package)))
                if self.ShowExternals:
                    for dep2 in package.ResolvedDirectExternalDependencies:
                        if not self.IsExternalAvailableFromDependentPackage(dep2, package.ResolvedDirectDependencies):
                            dotFile.append('  "%s" -> "ext: %s"' % (self.GetName(package), dep2.Name))

        if len(laterPrivate):
            dotFile.append('  edge [color="#2F4F4F", style=dashed]')
            for entry in laterPrivate:
                dotFile.append(entry)

        if len(laterLink):
            dotFile.append('  edge [color=Blue, style=dotted]')
            for entry in laterLink:
                dotFile.append(entry)

        dotFile.append('}')
        return dotFile


    def IsAvailableFromDependentPackage2(self, dep: PackageDependency, package: Package) -> bool:
        for entry in package.ResolvedAllDependencies:
            if entry.Name != dep.Name and entry.Access == AccessType.Public:
                if self.ExistIn(entry.Package.ResolvedAllDependencies, dep.Name):
                    return True
        return False


    def ExistIn(self, dependencies: Union[List[PackageDependency], List[PackageExternalDependency]], name: str) -> bool:
        for dep in dependencies:
            if dep.Name == name and dep.Access == AccessType.Public:
                return True
        return False

    def GetName(self, package: Package) -> str:
        if self.UseVariantNames:
            if package.ResolvedMakeVariantNameHint is None:
                raise Exception("Invalid package")
            return package.Name + package.ResolvedMakeVariantNameHint
        return package.Name


    def FilterBasedOnExecutableDemand(self, packages: List[Package]) -> List[Package]:
        executablePackages = []  # type: List[Package]
        for package in packages:
            if package.Type == PackageType.Executable:
                executablePackages.append(package)

        packageList = list(executablePackages)
        interestingPackages = set()  # type: Set[str]
        for package in executablePackages:
            for dep in package.ResolvedAllDependencies:
                if not dep.Name in interestingPackages:
                    interestingPackages.add(dep.Name)
                    packageList.append(dep.Package)
        return packageList