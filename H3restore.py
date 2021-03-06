#"THE BEER-WARE LICENSE" (Revision 42):
# <vysakhpillai@gmail.com> wrote this file. 
# As long as you retain this notice you can do whatever you want with this stuff. 
# If we meet some day, and you think this stuff is worth it, you can buy me a beer in return 
#                                                                        —※Vysakh P Pillai※

import glob, os,sys
import argparse
import git
import re
from colorama import init, Fore, Back, Style
import yaml
from lxml import etree
from datetime import datetime
import platform
import pprint

specialRepos=['contentmanager']
__version__="v1.6.1"

#Check if you are indeed in a git repo
def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

# pretty print the current versions
def print_versions(repos,manifest=None):
    if not bool(repos):
        print(Fore.RED+Style.BRIGHT+"No repos found in path.")
        sys.exit(-1)
    if manifest:
        print (Back.LIGHTBLUE_EX+"{:<35} {:<20} {:<20} {:<24} {:<15}".format('Repo','Current Version','Manifest Version','Latest version', 'Status'))
    else:
        print (Back.LIGHTBLUE_EX+"{:<35} {:<20} {:<24} {:<15}".format('Repo','Current Version','Latest Version', 'Status'))

    lineCount=0
    for k, v in repos.items():
        lineCount+=1;        
        if(v['cTag']!=v['lTag']):
            LineCol=Fore.YELLOW
        else:
            LineCol=Fore.GREEN

        manifestVer="N/A"
        if "manifestVer" in v.keys():
            if(v['cTag']!=v['manifestVer']):
                LineCol=Fore.RED
            manifestVer=v['manifestVer']

        cleanStat=Fore.GREEN+"Clean"
        if "cleanStat" in v.keys():
            if not v["cleanStat"]:
                cleanStat=Fore.RED+"Modified"

        background=""
        #if lineCount%2:
        #    background=Back.LIGHTBLACK_EX

        if manifest:
            print (background+LineCol+Style.BRIGHT+"{:<40} {:<20} {:<20} {:<20} {:13}".format(k,v["cTag"],manifestVer,v["lTag"],cleanStat))
        else:
            print (background+LineCol+Style.BRIGHT+"{:<40} {:<20} {:<20} {:<15}".format(k,v["cTag"],v["lTag"],cleanStat))
    print('\n\n')

#find the latest tag matching the Harmony3 semver pattern. Need to do this since some repos like cryptoauth lib has versions like 20210514
#  This is a workaround since passing the --list v* option with --sort=creatordate is causing issues eventhough it works in the cli
def get_last_semver(tags):
    #this is slightly modified from the regex provided by https://semver.org/ by enforcing a starting 'v'
    verPattern=r'^v(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    for version in tags[::-1]:
        if (re.search(verPattern,version)):
            return version        
    return "unknown"

def processPackage(packagePath):
    if not os.path.isfile(packagePath):
        print(Fore.RED+"Package file does not exist.")
        sys.exit(-4)
    packageTree = etree.parse(packagePath)
    package=packageTree.getroot()
    dependencies=package.findall('Dependencies/Dependency')
    manifest={}
    for dependency in dependencies:
        manifest[dependency.attrib['name']]=dependency.attrib['version']
    return manifest

def processManifest(manifestPath):
    if not os.path.isfile(manifestPath):
        print(Fore.RED+"Manifest file does not exist.")
        sys.exit(-3)
    manifest={}
    with open(manifestPath) as manifestFile:
        manifestEntries = yaml.load(manifestFile, Loader=yaml.FullLoader)["modules"]    
        for entry in manifestEntries:
            manifest[entry["name"]]=entry["version"]
    return manifest

# clean and restore the versions of all the repos
def restore_versions(repos,noclean):
    for k, v in repos.items():
        print(f'{Fore.LIGHTYELLOW_EX}> {k}{Fore.RESET}(', end='')
        if noclean:
            git.Repo(v["path"]).git.reset("--hard")
            print(f'{Fore.GREEN}reset{Fore.RESET},', end='')
            git.Repo(v["path"]).git.clean("-xfd")
            print(f'{Fore.GREEN}clean{Fore.RESET}',end='')
        
        if "manifestVer" not in v.keys():        
            if(v["cTag"]!=v["lTag"]):
                if("unknown"!=v["lTag"]):
                    print(f',{Fore.GREEN} checkout {Fore.LIGHTCYAN_EX}{v["lTag"]}{Fore.RESET}',end='')
                    try:
                        git.Repo(v["path"]).git.checkout(v["lTag"])
                    except Exception as e:
                        print(f'\n{Fore.RED} Git Error \n {e}')
                else:
                    pass
        else:
            if(v["cTag"]!=v["manifestVer"]):
                print(f',{Fore.GREEN} checkout {Fore.LIGHTCYAN_EX}{v["manifestVer"]}{Fore.RESET}',end='')
                try:
                    git.Repo(v["path"]).git.checkout(v["manifestVer"])
                except Exception as e:
                    print(f'\n{Fore.RED} Git Error \n {e}')
        print(f')')

def check_clean(repo):
    if not git.Repo(repo).git.status("--porcelain"):
        return True
    else:
        return False

#get details of the repos 
def get_repos(path,fetch=False,manifest=None):
    repos={}
    for repo in glob.iglob(os.path.abspath(path)+'\\**', recursive=False):
        if(is_git_repo(repo)):
            if os.path.basename(repo) in specialRepos:
                continue
            if fetch:
                print(f' > Fetching latest from {Fore.LIGHTBLUE_EX}{os.path.basename(repo)}')
                git.Repo(repo).git.fetch()
            repos[os.path.basename(repo)]={}
            repos[os.path.basename(repo)]["path"]=repo
            repos[os.path.basename(repo)]["cTag"]=(git.Repo(repo).git.describe("--match=v*"))
            repos[os.path.basename(repo)]["lTag"]=get_last_semver((git.Repo(repo).git.tag("--sort=creatordate").split('\n')))
            repos[os.path.basename(repo)]["cleanStat"]=check_clean(repo)
            if manifest:
                if os.path.basename(repo) in manifest.keys():
                    repos[os.path.basename(repo)]["manifestVer"]=manifest[os.path.basename(repo)]
    return repos
    
def generate_manifest(repos):
    manifestData={}
    manifestData["project"]="H3Restore"
    manifestData["creation_date"]=datetime.now().isoformat()
    manifestData["operating_system"]=f'{platform.system()} {platform.release()}'
    manifestData["mhc_mode"]="Standalone"
    manifestData["mhc_version"]=repos["mhc"]["cTag"]
    manifestData["compiler"]=None
    manifestData["modules"]=[]

    for k, v in repos.items():
        entry={}
        entry["name"]=k
        entry["version"]=v["cTag"]
        manifestData["modules"].append(entry)
    with open("harmony-manifest-success.yml", "w") as file:
        file.write(f"# This file was created using H3restore tool {__version__}\n")
        file.write("# For source code, refer to https://github.com/vppillai/H3Restore \n\n")
        yaml.dump(manifestData,file)

# check if Git is available. 
def check_git():
    try:
        git.cmd.Git().version()
    except Exception as e:
        print(Fore.RED+"Can't execute git commands. Make sure Git is installed and available in your PATH\n")
        sys.exit(-5)

if __name__ == "__main__":
    init(autoreset=True)
    parser = argparse.ArgumentParser(
        description=f"Tool to restore Harmony3 Git repos to the latest tag {Fore.LIGHTMAGENTA_EX}{__version__}{Fore.RESET}", prog="H3restore")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p', '--path', dest='path', help='Location of Harmony3 repo', required=True)
    parser.add_argument('-l', '--list', dest='list', default=False,action='store_true', help='Just list the changes. do not move the tags')
    parser.add_argument('-C', '--noclean', dest='clean', default=True,action='store_false', help='Do not clean and reset the repos. Might result in failures if there are uncommitted changes interfering with the tag change')
    parser.add_argument('-F', '--nofetch', dest='fetch', default=True,action='store_false', help='Do not fetch latest repo versions from origin')
    parser.add_argument('-x', '--manifestOut', dest='manifestOut',default=False,action='store_true', help='Generate a manifest file with the final configuration')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--manifest', dest='manifest', help='manifest file to be used to restore repos. Takes precedence over fetched versions')
    group.add_argument('-k', '--package', dest='package', help='package file to be used to restore repos. Takes precedence over fetched versions')
    
    args = parser.parse_args()

    check_git()

    manifest=None
    if args.manifest:
        manifest=processManifest(args.manifest)
    elif args.package:
        manifest=processPackage(args.package)
 
    print(Fore.YELLOW+"Checking repo details\n")
    repos=get_repos(args.path,fetch=args.fetch,manifest=manifest)
    
    print_versions(repos, manifest)
    if(args.list):
        print(Fore.YELLOW+Style.BRIGHT+"No repos have been been updated due to the -l flag")
        if args.manifestOut:
            print(Fore.YELLOW+"\nCreting local manifest file\n")
            generate_manifest(repos)    
        sys.exit(-2)

    restore_versions(repos,args.clean)
    print(Fore.YELLOW+"\n\nResults after the process:\n")

    upRepos=get_repos(args.path,manifest=manifest)
    print_versions(upRepos, manifest)

    if args.manifestOut:
        print(Fore.YELLOW+"\r\nCreting local manifest file\n")
        generate_manifest(upRepos)