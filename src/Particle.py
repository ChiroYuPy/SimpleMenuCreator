import math
import random

import pygame

from src.Config import *


class ParticleEmitter:
    def __init__(self, screen, particle_type, num_particles, particle_color1, particle_color2, particle_size,
                 particle_speed):
        self.screen = screen
        self.particle_type = particle_type
        self.num_particles = num_particles
        self.particle_color1 = particle_color1
        self.particle_color2 = particle_color2
        self.particle_size = particle_size
        self.particle_speed = particle_speed
        self.particles = []
        self.clock = pygame.time.Clock()

    class Particle:
        def __init__(self, x, y, size, speed, angle, color):
            self.x = x
            self.y = y
            self.size = size
            self.speed = speed
            self.angle = angle
            self.color = color

        def reset_pos(self):
            self.y = random.randrange(HEIGHT - 100, HEIGHT + 100)
            self.x = random.randrange(WIDTH)

    def start_snowfall(self):
        for _ in range(self.num_particles):
            x = random.randrange(WIDTH)
            y = random.randrange(HEIGHT + 200)
            angle = random.uniform(math.pi, math.pi * 2)

            # Interpolation linéaire entre particle_color1 et particle_color2
            t = random.uniform(0, 1)
            r = int((1 - t) * self.particle_color1[0] + t * self.particle_color2[0])
            g = int((1 - t) * self.particle_color1[1] + t * self.particle_color2[1])
            b = int((1 - t) * self.particle_color1[2] + t * self.particle_color2[2])
            color = (r, g, b)

            particle = self.Particle(x, y, random.randint(self.particle_size / 2, self.particle_size),
                                     self.particle_speed, angle, color)
            self.particles.append(particle)

    def update(self):
        time_step = 0.1

        for particle in self.particles:
            particle.y += particle.speed * time_step

            if particle.y > HEIGHT:
                particle.y -= HEIGHT

            particle.x += particle.speed * math.cos(particle.angle) * time_step
            particle.angle += 1 * time_step * 0.2

    def draw(self):
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.color, (int(particle.x), int(particle.y)), particle.size)
