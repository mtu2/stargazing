import math
import random
import time
from typing import List

DEFAULT_STARS = ["            ° .         °     °    +  ° .    , *         .     .                        ",
                 "        .°         o     ..  ° °       ° ,    ° .  o    ° *    ° . o. ° . .             ",
                 "                °     .      °     .   .°o  °  *  . ° .. * .  + . .    .                ",
                 " ° .    . .     .     .     ° °, *  ° .   +    ° ° ,° . °    , .°                       ",
                 "        °    °     °      .      + °   °  *    ° .  ,          + .    ° * °  ° .        ",
                 " °      .       . °     .  ° *    °,    ´ ° .       *   .      +  °  .°    .    ｡     . ",
                 "    .     °    °     °,    .°o  *   +   ,       *  ° .   °   ° .        °        .      ",
                 " ' .° °           +   ° .  +  °   *      ° . ,    , +     . °  . .     ,                ",
                 "    ° + ° `  ,  o    .°   *       ° . °    °  * +     ° .  °    ° .     ,            °  ",
                 "    .     °    °     °,    .°o  *   +   ,       *  ° .   °   ° .        °        .      ",
                 "         °         ° .° *  °      .      + °   °  *    ° .  ,          + .    ° * °  ° .",
                 " °      .       . °     .  ° *    °,    ´ ° .       *   .      +  °  .°    .    ｡     . ",
                 "    .     °    °     °,    .°o  *   +   ,       *  ° .   °   ° .        °        .      ",
                 " ° .° °           +   ° .  +  °  *        . , ,  +     . °  . .     ,                   ",
                 " °, .     +   * ° , ° .  o°   ° +      .,     . °     ,     °          °                ",
                 "           ° .   ⚹    *   °      ° . °            + °     °              °              "]


class StarsGenerator():
    """Generates printable stars for the backgorund of stargazing."""

    def __init__(self) -> None:
        self.stars = DEFAULT_STARS
        self.last_printed_time = 0

        self.gen_time_interval = 5
        self.gen_random_threshold = 0.1
        self.gen_max_dist = 5

    def get_stars(self) -> List[str]:
        curr_time = time.time()
        if curr_time - self.last_printed_time > self.gen_time_interval:
            self.last_printed_time = curr_time
            self.stars = self.gen_new_stars()

        return self.stars

    def gen_new_stars(self) -> List[str]:
        new_stars = []

        for line in self.stars:
            chars = list(line)
            for i in range(len(chars)):
                if random.random() < self.gen_random_threshold:
                    swap_dist = math.ceil(random.random() * self.gen_max_dist)
                    swap_i = (i + swap_dist) % len(chars)
                    chars[i], chars[swap_i] = chars[swap_i], chars[i]

            new_stars.append("".join(chars))

        return new_stars
