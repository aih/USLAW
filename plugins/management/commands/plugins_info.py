# -*- coding: utf-8 -*-
# Uslaw Project
# 

from colorama import init
from colorama import Fore, Back, Style

from django.core.management.base import BaseCommand
from django.conf import settings

from plugins.models import Plugin


class Command(BaseCommand):
    help = """Display information about installed plugins"""
    def handle(self, *args, **options):

        plugins = Plugin.objects.filter().order_by("plugin_id")
        print "%s >>Plugins list: %s" % (Fore.RED, Fore.RESET)
        for p in plugins:
            print "%s Plugin: %s %s %s Command: %s, ID: %s " % (Back.WHITE+Fore.BLACK, Style.BRIGHT+Fore.BLUE, p.name, Style.DIM+Fore.BLACK, p.plugin_command, p.plugin_id)
            if p.description:
                print "   +-[Description]"+"-"*60+">"
                print "   | ", p.description.replace("\n", "\n   | ")
                print "   +-"+"-"*73+">"
                print
        print Style.RESET_ALL
        print
