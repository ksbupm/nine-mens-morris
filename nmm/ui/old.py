

from dataclasses import dataclass, field
from typing import Tuple, List, Dict
from enum import Enum, auto

    
class Circle():
    def __init__(self, piece:Piece):
        self.piece = piece
        self.highlighted = False
    
    def draw(self, screen, config:UIConfig):
        pg.draw.circle(screen, 
                       {Player.AI: config.p1_color,
                        Player.HU: config.p2_color}[self.piece.owner],
                       config.positions[self.piece.position],
                       config.diameter // 2,
                       width=0)
        pg.draw.circle(screen, 
                       config.background,
                       config.positions[self.piece.position],
                       config.diameter // 2,
                       width=5)
        
        if self.highlighted:
            # glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            # pygame.draw.circle(glow_surface, (*glow_color, 100), (glow_radius, glow_radius), glow_radius)  # Semi-transparent glow

            # # Blit the glow surface
            # screen.blit(glow_surface, (circle_pos[0] - glow_radius, circle_pos[1] - glow_radius))
            ...
        
