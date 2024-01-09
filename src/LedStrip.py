
from abc import ABC, abstractmethod
from time import sleep

class ColorProvider(ABC):
    @abstractmethod
    def getColor(self, led: int) -> str:
        pass
    
class AllLedsSameColor(ColorProvider):
    def __init__(self, colorRGB : tuple):
        """Sets all leds to the same color
        param color: the color as RGB tuple
        """
        self.colorRGB = colorRGB
    
    def getColor(self, led: int) -> tuple:
        return self.colorRGB


class LedSwitch:
    @abstractmethod
    def on(self, leds: list, color : ColorProvider) -> None:
        """Turn on the leds given in the list""" 
        pass
    
    @abstractmethod
    def off(self, leds: list) -> None:
        """Turn off the leds given in the list""" 
        pass


class LedStrip:
    def __init__(self, allLeds : list, switch : LedSwitch):
        self.switch = switch
        self.allLeds = allLeds
            
    def allOff(self):
        """Turns all leds off in one go"""
        self.switch.off(self.allLeds)
        
    def allOn(self, color : ColorProvider):
        """Turns all leds off in one go"""
        self.switch.on(self.allLeds, color)
        
    def race(self, leds1: list, leds2: list, keepOnWhileRacing: bool, delayMs: int,
             colorProvider: ColorProvider, offAfterDone = True):
        
        for idx in range(max(len(leds1), len(leds2))):    
            leds = [leds1[min(idx, len(leds1) - 1)], leds2[min(idx, len(leds2) - 1)]]
            self.switch.on(color=colorProvider, leds=leds)
            sleep(delayMs / 1000)
            if not keepOnWhileRacing:
                self.switch.off(leds)
                
        sleep(delayMs / 1000)
        
        if keepOnWhileRacing and offAfterDone:
            self.switch.off(leds1+leds2)


